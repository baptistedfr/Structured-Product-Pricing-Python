import numpy as np
import pandas as pd
from scipy.optimize import minimize
from .abstract_volatility_surface import VolatilitySurface

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

    def __init__(self):
        self.svi_params = None

    @staticmethod
    def svi_total_variance(k: float, svi_params: np.ndarray) -> float:
        """
        Defines the SVI total implied variance w(k).

        Parameters:
            k (float): log moneyness
            svi_params (np.ndarray): five parameters of the SVI [a, b, p, m, sigma]

        Returns:
            float: total implied variance for this log moneyness level
        """
        a, b, rho, m, sigma = svi_params
        return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))


    def cost_function_svi(self, svi_params: np.ndarray, log_moneyness : np.ndarray, maturities: np.ndarray, market_implied_vol: np.ndarray):
        """
        Defines the MSE cost function for the optimization problem.
        We want to minimize the SVI fitting error :
            i.e. the gap between SVI total implied variance and market data total implied variance.

        Parameters:
            svi_params (np.ndarray): given set of svi parameters [a, b, p, m, sigma]
            log_moneyness (np.ndarray): market data log moneyness
            maturities (np.ndarray): market data maturities
            market_implied_vol (np.ndarray): market data implied volatility from the option data historic

        Returns:
            float: Mean Squared Error between market data and SVI total implied variance
        """
        # Conversion from market data implied volatility to market data total implied variance
        market_total_implied_variance = (market_implied_vol ** 2) * maturities

        # SVI total implied variance
        SVI_total_implied_variance = np.array([self.svi_total_variance(np.log(k / 100), svi_params) for k in log_moneyness])
        
        return np.sum((SVI_total_implied_variance - market_total_implied_variance) ** 2)


    def calibrate_surface(self, option_data: pd.DataFrame) -> None:
        """
        Calibrate the volatility surface with the option data by minimizing the fit error of the curve.

        We use the Nelder-Mead optimizer of scipy optimisation module.
        The initial parameters are those found by Axel Vogt (see Arbitrage-free SVI volatility surfaces - Gatheral 2024)

        Market option data has to contain at least 3 columns : 'Log Moneyness', 'Maturities' & 'Implied vol'
        """
        required_columns = {'Log Moneyness', 'Maturities', 'Implied vol'}
        if not required_columns.issubset(option_data.columns):
            raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

        initial_params = np.array([-0.0410, 0.1331, 0.3586, 0.3060, 0.4153])
        result = minimize(self.cost_function_svi, initial_params, method="Nelder-Mead",
                          args=(np.array(option_data["Log Moneyness"]),
                                np.array(option_data["Maturities"]),
                                np.array(option_data["Implied vol"])))
        
        self.svi_params = result.x


    def get_volatility(self, strike: float, maturity: float):
        """
        Get the volatility interpolated by the volatility surface at this specific point (Strike * Maturity).
        Params:
            strike (float): option strike
            maturity (float): option maturity in year

        Returns:
            float: volatility at this point of the surface
        """
        ...
