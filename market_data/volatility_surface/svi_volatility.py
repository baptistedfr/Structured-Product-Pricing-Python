import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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


    def __init__(self, option_data: pd.DataFrame):
        self.svi_params = None
        self.option_data = option_data


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
        SVI_total_implied_variance = np.array([self.svi_total_variance(np.log(k / 215), svi_params) for k in log_moneyness])
        
        return np.sum((SVI_total_implied_variance - market_total_implied_variance) ** 2)


    def calibrate_surface(self) -> None:
        """
        Calibrate the volatility surface with the option data by minimizing the fit error of the curve.

        We use the Nelder-Mead optimizer of scipy optimisation module.
        The initial parameters are those found by Axel Vogt (see Arbitrage-free SVI volatility surfaces - Gatheral 2024)

        Market option data has to contain at least 3 columns : 'Log Moneyness', 'Maturities' & 'Implied vol'
        """
        option_data = self.option_data

        required_columns = {'Strike', 'Spot', 'Maturity', 'Implied vol'}
        if not required_columns.issubset(option_data.columns):
            raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

        initial_params = np.array([-0.0410, 0.1331, 0.3586, 0.3060, 0.4153])

        option_data["Log Moneyness"] = np.log(option_data['Strike']/ option_data['Spot'])
        result = minimize(self.cost_function_svi, initial_params, method="Nelder-Mead",
                          args=(np.array(option_data["Log Moneyness"]),
                                np.array(option_data["Maturity"]),
                                np.array(option_data["Implied vol"])))
        
        self.svi_params = result.x


    def get_volatility(self, strike: float, maturity: float, spot: float) -> float:
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

        log_moneyness = np.log(strike / spot)
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
        vol_impl = [self.get_volatility(strike, maturity, spot) for strike in strikes]

        # Display the options
        if display_options:
            sub_calls = option_data[option_data["Type"] == "call"]
            sub_puts = option_data[option_data["Type"] == "put"]
            plt.scatter(sub_calls['Strike'], sub_calls['Implied vol'], color="royalblue", label='Calls')
            plt.scatter(sub_puts['Strike'], sub_puts['Implied vol'], color="crimson", label='Puts')

        # Display the smile
        plt.plot(strikes, vol_impl, label='SVI', color="teal")
        plt.xlabel('Strike')
        plt.grid(True)
        plt.ylabel('Implied Volatility')
        plt.title('Implied Volatility Smile')
        plt.show()


    def display_surface(self) -> None:
        """
        Displays the SVI volatility surface.
        """
        if self.svi_params is None:
            raise Exception("SVI surface not calibrated yet !")

        # Option data
        spot = self.option_data["Spot"].values[0]
        strikes = np.linspace(spot/2, spot*2, 50)
        maturities = np.linspace(min(self.option_data["Maturity"]), max(self.option_data["Maturity"]), 50)

        # Get the surface
        vol_surface = np.zeros((len(strikes), len(maturities)))
        for i, strike in enumerate(strikes):
            for j, maturity in enumerate(maturities):
                total_variance = self.get_volatility(strike, maturity, spot)
                vol_surface[i, j] = np.sqrt(total_variance / maturity)

        # Plot the surface
        X, Y = np.meshgrid(strikes, maturities)
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(Y, X, vol_surface, cmap='plasma')
        ax.set_xlabel('Strike')
        ax.set_ylabel('Maturity')
        ax.set_zlabel('Implied Volatility')
        ax.set_title('Implied Volatility Surface')
        plt.show()
