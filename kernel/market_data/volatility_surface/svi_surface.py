import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import seaborn as sns
from scipy.interpolate import interp1d
from kernel.market_data import RateCurve
from . import AbstractVolatilitySurface


class SVIVolatilitySurface(AbstractVolatilitySurface):
    """
    Defines the SVI raw parametrisation defined by Jim Gatheral (2004) to fit an arbitrage free Implied Volatility surface.

    We choose the "raw" parametrisation as it is the simplest SVI form by we note that "natural" or "jump wings"
    parametrisation can we derived from the raw form to insure parameters interpretability.
    All of those parametrisation are strictly equivalent.

    SVI models the total implied variance defined by :
        w(k, t) = σ(k, t)^2 * t.
    Where :
        - t is the maturity
        - k is the log moneyness (not the strike)

    And the implied variance is derived as :
        v(k, t) = σ(k, t)^2 = w(k, t) / t

    We shall refer to the two-dimensional map (k, t) → w(k, t) as the volatility surface,
    and for any fixed maturity t > 0, the function k → w(k, t) will represent a slice (volatility smile).
    For a given maturity slice, we shall use the notation w(k; χ) where χ represents a set of parameters, and drop the t-dependence.

    The parametrisation we use is defined by the five following parameters giving the total implied variance for any k :
        - a : level of variance, defines a smile vertical translation
        - b : smile slope level
        - p : counter-clockwise smile rotation
        - m : smile right translation
        - sigma : ATM smile curvature
    """

    def __init__(self, option_data: pd.DataFrame, rate_curve: RateCurve):
        """
        Parameters:
            option_data (pd.DataFrame): option market data, must contain the following columns : 'Strike', 'Spot', 'Maturity', 'Implied Volatility'
            rate_curve (RateCurve): rate curve object already calibrated
        """
        self.option_data = option_data
        self.spot = option_data["Spot"].values[0]
        self.svi_params = None
        self.rate_curve = rate_curve
        self.svi_params_by_maturity = {}
        self.interpolators = {}
        self.is_calibrated = False

    @staticmethod
    def svi_total_variance(k: np.ndarray[float], svi_params: np.ndarray[float]) -> float:
        """
        Defines the SVI total implied variance w(k).

        Parameters:
            k (np.ndarray[float]): log moneyness
            svi_params (np.ndarray[float]): five parameters of the SVI [a, b, p, m, sigma]

        Returns:
            float: total implied variance for this log moneyness level
        """
        a, b, rho, m, sigma = svi_params
        return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))

    def compute_weighting_vega(self, spot: float, maturities: np.ndarray[float],
                               vols: np.ndarray[float], strikes: np.ndarray[float]) -> np.ndarray[float]:
        """
        Compute vegas to weight the cost function in order to fit better the ATM options.

        Parameters:
            spot (np.ndarray[float]): market data spot
            maturities (np.ndarray[float]): market data maturities
            vols (np.ndarray[float]): market data Implied Volatility from the option data historic
            strikes (np.ndarray[float]): market data strikes

        Returns:
            np.ndarray[float]: options vega
        """
        try:
            r = np.array([self.rate_curve.get_rate(t) for t in maturities])/100
        except Exception:
            r = 0

        vols = vols / 100
        d1 = (np.log(spot / strikes) + (r + 0.5 * vols ** 2) * maturities) / (vols * np.sqrt(maturities))
        return spot * norm.pdf(d1) * np.sqrt(maturities)

    def cost_function_svi(self, svi_params: np.ndarray[float], log_moneyness : np.ndarray[float],
                          maturities: np.ndarray[float], market_implied_vol: np.ndarray[float],
                          vega: np.ndarray[float]) -> float:
        """
        Defines the MSE cost function for the optimization problem.
        We want to minimize the SVI fitting error :
            i.e. the gap between SVI total implied variance and market data total implied variance.

        Parameters:
            svi_params (np.ndarray[float]): given set of svi parameters [a, b, p, m, sigma]
            log_moneyness (np.ndarray[float]): market data log moneyness
            maturities (np.ndarray[float]): market data maturities
            market_implied_vol (np.ndarray[float]): market data Implied Volatility from the option data historic
            vega (np.ndarray[float]): vega to weight the MSE by putting more importance on ATM options

        Returns:
            float: Mean Squared Error between market data and SVI total implied variance
        """
        # Conversion from market data Implied Volatility to market data total implied variance
        market_total_variance = (market_implied_vol ** 2) * maturities

        # SVI total implied variance
        SVI_total_variance = np.array(self.svi_total_variance(log_moneyness, svi_params))

        return float(np.mean((SVI_total_variance - market_total_variance) ** 2))

    def calibrate_surface(self) -> None:
        """
        Calibrate the volatility surface by fitting SVI parameters for each maturity slice,
        then interpolate the parameters across maturities.
        """
        unique_maturities = self.option_data["Maturity"].unique()
        self.svi_params_by_maturity = {}

        for maturity in unique_maturities:
            # Filter data for the current maturity
            slice_data = self.option_data[self.option_data["Maturity"] == maturity]
            log_moneyness = np.log(slice_data['Strike'].values / self.spot)
            market_vols = slice_data["Implied Volatility"].values / 100
            strikes = slice_data["Strike"].values

            # Compute vega weights
            vega = self.compute_weighting_vega(self.spot,
                                               slice_data["Maturity"].values,
                                               market_vols,
                                               strikes)

            # Initial parameters and bounds
            initial_params = np.array([0.1, 0.1, 0.0, 0.0, 0.1])
            bounds = [(0, None), (0, None), (-1, 1), (None, None), (0, None)]

            # Perform optimization
            result = minimize(self.cost_function_svi, initial_params, method="L-BFGS-B", bounds=bounds,
                              args=(log_moneyness, slice_data["Maturity"].values, market_vols, vega))

            if result.success:
                self.svi_params_by_maturity[maturity] = result.x
                self.is_calibrated = True
            else:
                raise Exception(f"SVI calibration failed for maturity {maturity}: {result.message}")

        # Interpolate SVI parameters across maturities
        self._interpolate_parameters(unique_maturities)

    def _interpolate_parameters(self, maturities: np.ndarray) -> None:
        """
        Interpolate SVI parameters across maturities.
        """
        svi_params_array = np.array([self.svi_params_by_maturity[m] for m in maturities])
        self.interpolators = {
            i: interp1d(maturities, svi_params_array[:, i], kind='cubic', fill_value="extrapolate")
            for i in range(5)
        }

    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Get the volatility interpolated by the volatility surface at this specific point (Strike * Maturity).

        Parameters:
            strike (float): strike price
            maturity (float): maturity in years

        Returns:
            float: implied volatility
        """
        if not self.interpolators:
            raise Exception("SVI surface not calibrated yet!")

        # Handle flat extrapolation for maturities outside the calibrated range
        min_maturity = min(self.svi_params_by_maturity.keys())
        max_maturity = max(self.svi_params_by_maturity.keys())

        if maturity < min_maturity:
            interpolated_params = np.array([self.svi_params_by_maturity[min_maturity][i] for i in range(5)])
        elif maturity > max_maturity:
            interpolated_params = np.array([self.svi_params_by_maturity[max_maturity][i] for i in range(5)])
        else:
            interpolated_params = np.array([self.interpolators[i](maturity) for i in range(5)])

        log_moneyness = np.log(strike / self.spot)
        total_variance = self.svi_total_variance(log_moneyness, interpolated_params)
        return np.sqrt(total_variance / maturity)

    def display_smiles(self) -> None:
        """
        Displays the SVI volatility smiles for all maturities in the option data.
        Each subplot corresponds to a specific maturity and shows both market data and the interpolated smile.
        """
        if not self.interpolators:
            raise Exception("SVI surface not calibrated yet!")

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
            ax.set_ylabel('SVI Implied Volatility (%)', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.7)

        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

    def display_surface(self) -> None:
        """
        Displays the SVI volatility surface.
        """
        if not self.interpolators:
            raise Exception("SVI surface not calibrated yet!")

        spot = self.option_data["Spot"].values[0]
        strikes = np.linspace(spot / 2, spot * 2, 100)
        maturities = np.linspace(min(self.option_data["Maturity"]), max(self.option_data["Maturity"]), 100)

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
        ax.set_title('SVI Implied Volatility Surface', fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=10)

        plt.tight_layout()
        plt.show()
