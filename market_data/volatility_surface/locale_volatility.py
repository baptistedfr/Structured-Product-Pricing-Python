import pandas as pd
from .abstract_volatility_surface import VolatilitySurface

class LocaleVolatilitySurface(VolatilitySurface):

    def calibrate_surface(self, option_data: pd.DataFrame):
        """
        Calibrate the volatility surface with the option data by minimizing the fit error of the curve.
        """
        ...

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
