import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from . import AbstractVolatilitySurface
from kernel.market_data import RateCurve


class LocalVolatilitySurface(AbstractVolatilitySurface):
    """
    """

    def __init__(self, option_data: pd.DataFrame, rate_curve: RateCurve):
        """
        Parameters:
            option_data (pd.DataFrame): option market data, must contain the following columns : 'Strike', 'Price', 'Maturity'
            rate_curve (RateCurve): rate curve object already calibrated
        """
        self.option_data = option_data
        self.maturities_grid = None
        self.strikes_grid = None
        self.price_surface = None

    def calibrate_surface(self):
        """
        Calibrate the price surface with the option data.
        """
        option_data = self.option_data
        strikes = np.linspace(min(option_data["Strike"]), max(option_data["Strike"]), 50)
        maturities = np.linspace(min(option_data["Maturity"]), max(option_data["Maturity"]), 50)
        self.strikes_grid, self.maturities_grid = np.meshgrid(strikes, maturities)

        self.price_surface = griddata(points=(option_data["Strike"], option_data["Maturity"]),
                                      values=option_data["Price"],
                                      xi=(self.strikes_grid, self.maturities_grid),
                                      method='cubic')

    def _compute_derivatives(self, strike: float, maturity: float):
        """
        Compute the partial derivatives needed for the Dupire equation.
        """
        if self.price_surface is None:
            raise ValueError("Price surface not calibrated. Call calibrate_surface() first.")

        # Trouver les indices les plus proches
        strike_idx = (np.abs(self.strikes_grid[0] - strike)).argmin()
        maturity_idx = (np.abs(self.maturities_grid[:, 0] - maturity)).argmin()

        # Différences finies pour approximer les dérivées
        dt = np.gradient(self.maturities_grid[:, 0])
        dk = np.gradient(self.strikes_grid[0])

        dC_dT = np.gradient(self.price_surface, axis=0)[maturity_idx, strike_idx] / dt[maturity_idx]
        dC_dK = np.gradient(self.price_surface, axis=1)[maturity_idx, strike_idx] / dk[strike_idx]
        d2C_d2K = np.gradient(np.gradient(self.price_surface, axis=1), axis=1)[maturity_idx, strike_idx] / dk[
            strike_idx] ** 2

        return dC_dT, dC_dK, d2C_d2K

    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Get the local volatility from the Dupire equation at this specific point (Strike * Maturity).
        Params:
            strike (float): option strike
            maturity (float): option maturity in year

        Returns:
            float: volatility at this point of the surface
        """
        # Finite differences derivatives
        dC_dT, dC_dK, d2C_d2K = self._compute_derivatives(strike=strike, maturity=maturity)

        # Compute Dupire equation for the local variance
        local_variance = (dC_dT + strike * dC_dK) / (0.5 * strike**2 * d2C_d2K)
        return np.sqrt(local_variance)

    def display_smile(self) -> None:
        """
        Displays the local volatility smiles
        """
        ...

    def display_surface(self) -> None:
        """
        Displays the local volatility surface.
        """
        ...