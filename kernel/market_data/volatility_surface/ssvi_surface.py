import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import seaborn as sns
from scipy.interpolate import interp1d
from kernel.market_data import RateCurve
from . import AbstractVolatilitySurface


class SSVIVolatilitySurface(AbstractVolatilitySurface):
    """
    """

    def __init__(self, option_data: pd.DataFrame, rate_curve: RateCurve):
        """
        Parameters:
            option_data (pd.DataFrame): option market data, must contain the following columns : 'Strike', 'Spot', 'Maturity', 'Implied Volatility'
            rate_curve (RateCurve): rate curve object already calibrated
        """
        self.option_data = option_data
        self.rate_curve = rate_curve

        self.spot = option_data["Spot"].values[0]
        self.ssvi_params = None
        self.ssvi_ATM_params = None

    @staticmethod
    def _ssvi_atm_variance(maturity: np.ndarray[float], ssvi_atm_params: np.ndarray[float]) -> float:
        """
        SSVI total variance function.

        Parameters:
            maturity (np.ndarray[float]): maturity in years
            ssvi_atm_params (np.ndarray[float]): SSVI ATM variance parametrization parameters

        Returns:
            np.ndarray[float]: total variance
        """
        kappa, v0, v_inf = ssvi_atm_params

        return (((1 - np.exp(-kappa * maturity))/kappa * maturity) * (v0 - v_inf) + v_inf) * maturity
    
    @staticmethod
    def _ssvi_total_variance(k: np.ndarray[float], atm_variance: float, ssvi_params: np.ndarray[float]) -> float:
        """
        SSVI total variance function.

        Parameters:
            k (np.ndarray[float]): log moneyness
            atm_variance (float): ATM variance for the given maturity
            ssvi_params (np.ndarray[float]): SSVI parameters

        Returns:
            np.ndarray[float]: total variance
        """
        rho, eta, gamma = ssvi_params
        phi = lambda theta: eta * theta ** (-gamma)

        return 0.5 * atm_variance * ( 1 + rho * phi(atm_variance) * k + np.sqrt((phi(atm_variance) * k + rho)**2 + (1 - rho **2)))
    
    def _get_market_atm_variance(self, maturity: float) -> float:
        """
        Get the ATM variance for a given maturity from the option data.
        This function checks if an ATM option is available in the data.
        If not, it interpolates the ATM variance from the available options of the slice.

        Parameters:
            maturity (float): maturity in years

        Returns:
            float: ATM variance
        """
        # Filter the option data for the given maturity
        option_slice = self.option_data[self.option_data["Maturity"] == maturity]
        if option_slice.empty:
            raise ValueError(f"No option data available for maturity {maturity}")

        # If an ATM option is available, use its implied volatility
        atm_option = option_slice[option_slice["Strike"] == self.spot]
        if not atm_option.empty:
            return maturity * atm_option["Implied Volatility"] ** 2
        
        # Otherwise, interpolate the ATM variance from the option slice data
        else:
            atm_vol = np.interp(self.spot, option_slice["Strike"].values, option_slice["Implied Volatility"].values)
            return maturity * atm_vol ** 2
    
    def _get_atm_variance(self, maturity: float) -> float:
        """
        Get the ATM variance for a given maturity from the option data.

        Parameters:
            maturity (float): maturity in years

        Returns:
            float: ATM variance
        """
        if self.ssvi_ATM_params is None:
            raise ValueError("SSVI ATM parameters are not calibrated. Please call calibrate_atm_variance() first.")
        
        return self._ssvi_atm_variance(maturity, self.ssvi_ATM_params)
    
    def _ssvi_atm_cost_function(self, ssvi_atm_params: np.ndarray[float], maturities: np.ndarray[float], implied_ATM_variance: np.ndarray[float]) -> float:
        """
        Cost function for the SSVI ATM calibration.
        The calibration is done by minimizing the mean squared error between the market implied volatility and the SSVI model implied volatility.

        Parameters:
            ssvi_atm_params (np.ndarray[float]): SSVI ATM variance parametrization parameters
            maturities (np.ndarray[float]): maturities in years
            implied_ATM_variance (np.ndarray[float]): market implied ATM variance

        Returns:
            float: mean squared error between the market implied volatility and the SSVI model implied volatility for ATM options
        """
        ssvi_ATM_variance = self._ssvi_atm_variance(maturities, ssvi_atm_params)

        return np.mean((implied_ATM_variance - ssvi_ATM_variance) ** 2)
    
    def _ssvi_objective_function(self, ssvi_params: np.ndarray[float], option_data: pd.DataFrame) -> float:
        """
        Objective function for the SSVI calibration.
        The calibration is done by minimizing the mean squared error between the market implied volatility and the SSVI model implied volatility.
        For each maturity, the ATM variance is computed and used to compute the SSVI implied volatility.

        Parameters:
            ssvi_params (np.ndarray[float]): SSVI parameters
            option_data (pd.DataFrame): option market data, must contain the following columns : 'Strike', 'Spot', 'Maturity', 'Implied Volatility'

        Returns:
            float: mean squared error between the market implied volatility and the SSVI model implied volatility
        """
        ssvi_total_variance = []
        market_total_variance = []
        for maturity in option_data["Maturity"].unique():
            # Filter the option data for the given maturity
            slice_options = option_data[option_data["Maturity"] == maturity]

            # For each maturity, compute the ATM variance and the SSVI implied volatility
            atm_variance = self._get_atm_variance(maturity)
            
            k = np.log(slice_options["Strike"].values / self.spot)
            ssvi_total_variance.append(self._ssvi_total_variance(k, atm_variance, ssvi_params))

            # Also compute the market data total implied variance
            market_total_variance.append((slice_options["Implied Volatility"].values ** 2) * maturity)

        # Flatten the list of total variance arrays and market total variance arrays
        ssvi_total_variance = np.concatenate(ssvi_total_variance)
        market_total_variance = np.concatenate(market_total_variance)

        return np.mean((market_total_variance - ssvi_total_variance) ** 2)

    def calibrate_atm_variance(self):
        """
        Calibrate the ATM variance using the option data.
        This function uses the least squares method to minimize the difference between the market implied volatility and the SSVI model implied volatility at ATM.
        """
        maturities = self.option_data["Maturity"].unique()
        atm_market_variance = np.array([self._get_market_atm_variance(maturity) for maturity in maturities])

        # Calibrate the ATM variance wit ATM options
        initial_values = [0.1, 0.2, 0.2]  # Initial guess for the ATM parameters [kappa, v0, v_inf]

        res = minimize(
            self._ssvi_atm_cost_function,
            initial_values,
            args=(maturities, atm_market_variance),
            method="Nelder-Mead",
        )
        
        if res.success:
            self.ssvi_ATM_params = res.x
        else:
            raise Exception(f"SSVI ATM parametrization calibration failed : {res.message}")

    def calibrate_surface(self):
        """
        Calibrate the SSVI parameters using the option data.
        This function uses the least squares method to minimize the difference between the market implied volatility and the SSVI model implied volatility.
        
        The calibration is done for the whole maturity range of the option data.
        First we calibrate the ATM variance and then we calibrate the SSVI parameters.
        """
        # Calibrate the ATM variance first
        self.calibrate_atm_variance()

        # Initial guess for the SSVI parameters [rho, eta, gamma]
        initial_values = [0.1, 0.1, 0.1]

        res = minimize(
            self._ssvi_objective_function,
            initial_values,
            args=(self.option_data),
            method="Nelder-Mead",
        )

        if res.success:
            self.ssvi_params = res.x
        else:
            raise Exception(f"SSVI calibration failed : {res.message}")
        
    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Get the volatility interpolated by the SSVI model for a given strike and maturity.

        Parameters:
            strike (float): strike price
            maturity (float): maturity in years

        Returns:
            float: implied volatility
        """
        if self.ssvi_params is None:
            raise ValueError("SSVI parameters are not calibrated. Please call calibrate_surface() first.")

        atm_variance = self._get_atm_variance(maturity)

        k = np.log(strike / self.spot)
        ssvi_total_variance = self._ssvi_total_variance(k, atm_variance, self.ssvi_params)

        return np.sqrt(ssvi_total_variance / maturity) / 100
    
    def display_smiles(self):
        """
        Displays the SSVI volatility smiles for all maturities in the option data.

        Each subplot corresponds to a specific maturity and shows both market data and the interpolated smile.
        """
        if self.ssvi_params is None:
            raise ValueError("SSVI parameters are not calibrated. Please call calibrate_surface() first.")

        # Get unique maturities
        unique_maturities = self.option_data["Maturity"].unique()
        num_maturities = len(unique_maturities)

        # Create subplots
        cols = 4
        rows = (num_maturities + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
        axes = axes.flatten()

        for i, maturity in enumerate(unique_maturities):
            ax = axes[i]

            # Extract option data for the current maturity
            option_data = self.option_data[self.option_data["Maturity"] == maturity]
            spot = self.option_data["Spot"].values[0]
            strikes = np.linspace(spot / 2, spot * 2, 500)

            # Get the smile
            vol_impl = [self.get_volatility(strike, maturity) * 100 for strike in strikes]

            # Plot market data
            ax.scatter(option_data['Strike']*100/self.spot, option_data['Implied Volatility'], color='blue', label='Market Data', s=20)

            # Plot interpolated smile
            strikes = (strikes / self.spot) * 100
            ax.plot(strikes, vol_impl, label='Interpolated Smile', color='orange')

            # Set labels and title
            ax.set_title(f"Maturity: {int(maturity*252)} days", fontsize=12, fontweight='bold')
            ax.set_xlabel('Moneyness (% ATM)', fontsize=10)
            ax.set_ylabel('SSVI Implied Volatility (%)', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.7)

        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

    
    def display_surface(self) -> None:
        """
        Displays the SSVI volatility surface.
        """
        if self.ssvi_params is None:
            raise ValueError("SSVI parameters are not calibrated. Please call calibrate_surface() first.")

        spot = self.option_data["Spot"].values[0]
        strikes = np.linspace(spot / 2, spot * 2, 50)
        maturities = np.linspace(min(self.option_data["Maturity"]), max(self.option_data["Maturity"]), 50)

        # Get the surface
        vol_surface = np.zeros((len(strikes), len(maturities)))
        for i, strike in enumerate(strikes):
            for j, maturity in enumerate(maturities):
                vol_surface[i, j] = self.get_volatility(strike, maturity) * 100

        maturities = maturities * 252
        strikes = (strikes / self.spot) * 100
        X, Y = np.meshgrid(maturities, strikes)
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, vol_surface, cmap='viridis', edgecolor='k', alpha=0.8)

        option_strikes = (self.option_data["Strike"] / self.spot) * 100
        option_maturities = self.option_data["Maturity"] * 252
        option_vols = self.option_data["Implied Volatility"]
        ax.scatter(option_maturities, option_strikes, option_vols, color='red', label='Options', s=20)

        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
        cbar.set_label('Implied Volatility', fontsize=12)
        ax.set_xlabel('Maturity (days)', fontsize=12, labelpad=10)
        ax.set_ylabel('Moneyness (% ATM)', fontsize=12, labelpad=10)
        ax.set_zlabel('Implied Volatility (%)', fontsize=12, labelpad=10)
        ax.set_title('SSVI Implied Volatility Surface', fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=10)

        plt.tight_layout()
        plt.show()