import os
import numpy as np
import pandas as pd
from Kernel.tools import *
from Kernel.market_data import RateCurve, InterpolationType,UnderlyingAsset, VolatilitySurfaceType

class Market:
    """
    Represents a financial market environment, providing tools to fetch and use yield curves,
    compute interest rates, and discount factors.

    Attributes:
        rate_curve_type (RateCurveType): The type of rate curve to use (e.g., RF_US_TREASURY)
        interpolation_type (InterpolationType): The interpolation method for the rate curve (e.g., CUBIC)
        volatility_surface_type (VolatilitySurfaceType): The type of volatility surface to use (e.g., SVI)
        calendar_convention (CalendarConvention): The calendar convention for calculations (e.g., ACT_360)
        rate_curve (RateCurve): The rate curve object containing yield curve data and interpolation logic
    """

    def __init__(self, underlying_name: str, 
                 rate_curve_type: RateCurveType = RateCurveType.RF_US_TREASURY, 
                 interpolation_type: InterpolationType = InterpolationType.CUBIC,
                 volatility_surface_type: VolatilitySurfaceType = VolatilitySurfaceType.SVI,
                 calendar_convention: CalendarConvention = CalendarConvention.ACT_360):
        """
        Initializes the Market object with specified configurations.

        Parameters:
            rate_curve_type (RateCurveType): The type of rate curve to use
            interpolation_type (InterpolationType): The interpolation method for the rate curve
            volatility_surface_type (VolatilitySurfaceType): The type of volatility surface to use
            calendar_convention (CalendarConvention): The calendar convention for calculations
        """
        self.rate_curve_type = rate_curve_type
        self.interpolation_type = interpolation_type
        self.volatility_surface_type = volatility_surface_type
        self.calendar_convention = calendar_convention

        self.rate_curve = None
        self._fetch_yield_curves()

        self.underlying_asset = UnderlyingAsset(underlying_name)
        self._fetch_underlying_info()

        self.volatility_surface = None
        self._fetch_volatility_surface()

    def _fetch_yield_curves(self):
        """
        Fetches and initializes the yield curve data based on the specified rate curve type.

        Raises:
            Exception: If there is an error loading the yield curve data
        """
        if not os.path.exists(f"data/yield_curves/{self.rate_curve_type.value}"):
            raise FileNotFoundError(f"'data/yield_curves/{self.rate_curve_type.value}' does not exist.")
        else:
            data_curve = pd.read_excel(f"data/yield_curves/{self.rate_curve_type.value}")
        
        rate_curve = RateCurve(data_curve=data_curve, interpolation_type=self.interpolation_type)
        rate_curve.calibrate()

        self.rate_curve = rate_curve
        

    def _fetch_underlying_info(self):
        """
        Fetches and initializes the price of the underlying asset.

        Raises:
            Exception: Specific error message described in underlying_asset.py
        """
        self.underlying_asset.load_underlying_info()
        
    def _fetch_volatility_surface(self):

        if not os.path.exists(f"data/option_data/option_data_{self.underlying_asset.ticker}.xlsx"):
            raise FileNotFoundError(f"'data/option_data/option_data_{self.underlying_asset.ticker}.xlsx' does not exist.")
        else:
            option_data = pd.read_excel(f"data/option_data/option_data_{self.underlying_asset.ticker}.xlsx")
            option_data["Spot"] = self.underlying_asset.last_price

        required_columns = ["Strike", "Implied vol", "Maturity"]
        missing_columns = [col for col in required_columns if col not in option_data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        if self.rate_curve is None:
            self._fetch_yield_curves()

        volatility_surface = self.volatility_surface_type.value(option_data=option_data, rate_curve=self.rate_curve)
        volatility_surface.calibrate_surface()

        self.volatility_surface = volatility_surface

    def get_rate(self, maturity: float) -> float:
        """
        Retrieves the interest rate for a given maturity.

        Parameters:
            maturity (float): Desired maturity in years

        Returns:
            float: Interpolated yield rate
        """
        if not self.rate_curve:
            self._fetch_yield_curves()
        return self.rate_curve.get_rate(maturity)
    
    def get_discount_factor(self, maturity: float) -> float:
        """
        Computes the discount factor for a given maturity using the interpolated yield.

        Parameters:
            maturity (float): Desired maturity in years

        Returns:
            float: Discount factor
        """
        rate = self.get_rate(maturity)
        return np.exp(-rate * maturity)
    
    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Get the volatility interpolated by the volatility surface at this specific point (Strike * Maturity).
        Params:
            strike (float): option strike
            maturity (float): option maturity in year

        Returns:
            float: volatility at this point of the surface
        """
        if not self.volatility_surface:
            self._fetch_volatility_surface()
        return self.volatility_surface.get_volatility(strike, maturity)
