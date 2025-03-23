import pandas as pd
from abc import ABC, abstractmethod
from Kernel.market_data.rate_curve.rate_curve import RateCurve


class VolatilitySurface(ABC):

    def __init__(self, option_data: pd.DataFrame, rate_curve: RateCurve):
        """
        Parameters:
            option_data (pd.DataFrame): option market data, must contain the following columns : 'Strike', 'Price', 'Maturity'
            rate_curve (RateCurve): rate curve object already calibrated
        """
        self.option_data = option_data

    @abstractmethod
    def calibrate_surface(self) -> None:
        """
        Calibrate the volatility surface with the option data by minimizing the fit error of the curve.
        """
        ...

    @abstractmethod
    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Get the volatility interpolated by the volatility surface at this specific point (Strike * Maturity).
        Params:
            strike (float): option strike
            maturity (float): option maturity in year

        Returns:
            float: volatility at this point of the surface
        """
        ...

    @abstractmethod
    def display_smile(self, maturity: float, display_options: bool = True) -> None:
        """
        Displays the volatility smile for a given maturity.

        Parameters:
            maturity (float): maturity for which we display the smile
            display_options (bool): display the options on the smile plot or not
        """
        ...

    @abstractmethod
    def display_surface(self) -> None:
        """
        Displays the volatility surface.
        """
        ...