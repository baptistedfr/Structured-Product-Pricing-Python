import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from kernel.market_data.rate_curve.rate_curve import RateCurve
from .abstract_volatility_surface import VolatilitySurface
import seaborn as sns


class SVIVolatilitySurface(VolatilitySurface):
    """
    Defines the SVI raw parametrisation defined by Jim Gatheral (2004) to fit an arbitrage free implied volatility surface.

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
            option_data (pd.DataFrame): option market data, must contain the following columns : 'Strike', 'Spot', 'Maturity', 'Implied vol'
            rate_curve (RateCurve): rate curve object already calibrated
        """
        self.option_data = option_data
        self.spot = None
        self.svi_params = None
        self.rate_curve = rate_curve

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
            vols (np.ndarray[float]): market data implied volatility from the option data historic
            strikes (np.ndarray[float]): market data strikes

        Returns:
            np.ndarray[float]: options vega
        """
        # Interpol rates for the maturities
        try:
            r = np.array([self.rate_curve.get_rate(t) for t in maturities])/100
        except Exception:
            r = 0

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
            market_implied_vol (np.ndarray[float]): market data implied volatility from the option data historic
            vega (np.ndarray[float]): vega to weight the MSE by putting more importance on ATM options

        Returns:
            float: Mean Squared Error between market data and SVI total implied variance
        """
        # Conversion from market data implied volatility to market data total implied variance
        market_total_variance = (market_implied_vol ** 2) * maturities

        # SVI total implied variance
        SVI_total_variance = np.array(self.svi_total_variance(log_moneyness, svi_params))

        return float(np.mean(vega * (SVI_total_variance - market_total_variance) ** 2))

    def calibrate_surface(self) -> None:
        """
        Calibrate the volatility surface with the option data by minimizing the fit error of the curve.

        We use the Nelder-Mead optimizer of scipy optimisation module.

        Market option data has to contain at least 4 columns : 'Log Moneyness', 'Spot', 'Maturities' & 'Implied vol'
        """
        option_data = self.option_data

        required_columns = {'Strike', 'Spot', 'Maturity', 'Implied vol'}
        if not required_columns.issubset(option_data.columns):
            raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

        initial_params = np.array([0, 0, 0, 0, 0])
        option_data["Log Moneyness"] = np.log(option_data['Strike']/ option_data['Spot'])

        vega = self.compute_weighting_vega(option_data['Spot'].values[0],
                                           option_data["Maturity"], option_data["Implied vol"], option_data['Strike'])

        result = minimize(self.cost_function_svi, initial_params, method="BFGS",
                          args=(np.array(option_data["Log Moneyness"]),
                                np.array(option_data["Maturity"]),
                                np.array(option_data["Implied vol"]),
                                vega))
        
        self.svi_params = result.x
        self.spot = option_data['Spot'].values[0]

    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Get the volatility interpolated by the volatility surface at this specific point (Strike * Maturity).
        Params:
            strike (float): option strike
            maturity (float): option maturity in year

        Returns:
            float: volatility at this point of the surface
        """
        if self.svi_params is None:
            raise Exception("SVI surface not calibrated yet !")

        log_moneyness = np.log(strike / self.spot)
        total_variance = self.svi_total_variance(log_moneyness, self.svi_params)
        return np.sqrt(total_variance / maturity)

    def display_smile(self, maturity: float, display_options: bool = True) -> None:
        """
        Displays the SVI volatility smile for a given maturity.

        Parameters:
            maturity (float): maturity for which we display the smile
            display_options (bool): display the options on the smile plot or not
        """
        if self.svi_params is None:
            raise Exception("SVI surface not calibrated yet !")

        # Extract option data at the given maturity
        option_data = self.option_data[self.option_data["Maturity"] == maturity]
        spot = self.option_data["Spot"].values[0]
        strikes = np.linspace(spot/2, spot*2, 500)

        # Get the smile
        vol_impl = [self.get_volatility(strike, maturity) for strike in strikes]

        sns.set(style="whitegrid")
        palette = sns.color_palette("coolwarm", 3)
        # Display the options
        if display_options:
            sub_calls = option_data[option_data["Type"] == "call"]
            sub_puts = option_data[option_data["Type"] == "put"]
            plt.scatter(sub_calls['Strike'], sub_calls['Implied vol'], color=palette[0], label='Calls')
            plt.scatter(sub_puts['Strike'], sub_puts['Implied vol'], color=palette[1], label='Puts')

        # Display the smile
        plt.plot(strikes, vol_impl, label='SVI', color=palette[2])
        plt.xlabel('Strike', fontsize=12)
        plt.ylabel('Implied Volatility', fontsize=12)
        plt.title('Implied Volatility Smile', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def display_surface(self) -> None:
        """
        Displays the SVI volatility surface.
        """
        if self.svi_params is None:
            raise Exception("SVI surface not calibrated yet !")

        # Option data
        spot = self.option_data["Spot"].values[0]
        strikes = np.linspace(spot / 2, spot * 2, 50)
        maturities = np.linspace(min(self.option_data["Maturity"]), max(self.option_data["Maturity"]), 50)

        # Get the surface
        vol_surface = np.zeros((len(strikes), len(maturities)))
        for i, strike in enumerate(strikes):
            for j, maturity in enumerate(maturities):
                total_variance = self.get_volatility(strike, maturity)
                vol_surface[i, j] = np.sqrt(total_variance / maturity)

        # Plot the surface
        X, Y = np.meshgrid(strikes, maturities)
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(Y, X, vol_surface, cmap='viridis', edgecolor='k', alpha=0.8)

        # Add color bar
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
        cbar.set_label('Implied Volatility', fontsize=12)

        # Set labels and title
        ax.set_xlabel('Maturity', fontsize=12, labelpad=10)
        ax.set_ylabel('Strike', fontsize=12, labelpad=10)
        ax.set_zlabel('Implied Volatility', fontsize=12, labelpad=10)
        ax.set_title('Implied Volatility Surface', fontsize=14, fontweight='bold')

        # Add gridlines
        ax.grid(True, linestyle='--', alpha=0.5)

        plt.tight_layout()
        plt.show()
