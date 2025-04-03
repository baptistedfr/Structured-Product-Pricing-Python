import os
import numpy as np
import pandas as pd
from kernel.tools import *
from kernel.market_data import RateCurve, InterpolationType,UnderlyingAsset, VolatilitySurfaceType
import re

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

    @staticmethod
    def _convert_maturities(maturity: str) -> float:
        """
        Converts a maturity string (e.g., '10Y', '6M', '3W') into a numerical value in years.

        Parameters:
            maturity (str): Maturity in standard financial format (e.g., '10Y', '6M', '3W').

        Returns:
            float: Maturity expressed in years.
        """
        match = re.match(r"(\d+)([MWY])", maturity)
        if not match:
            raise ValueError(f"Invalid maturity: {maturity}")

        value, unit = int(match.group(1)), match.group(2)
        
        if unit == "W":
            return value / 52  # Convert weeks to years
        elif unit == "M":
            return value / 12  # Convert months to years
        elif unit == "Y":
            return value       # Already in years
        else:
            raise ValueError(f"Unrecognized unit: {unit}")
        
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
        
        required_columns = ["Maturity", "Rate"]
        missing_columns = [col for col in required_columns if col not in data_curve.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        data_curve["Maturity"] = data_curve["Maturity"].apply(self._convert_maturities)

        rate_curve = RateCurve(data_curve=data_curve, interpolation_type=self.interpolation_type)
        rate_curve.calibrate()

        self.rate_curve = rate_curve

    def _fetch_underlying_info(self, file_path: str = "data/underlying_data.xlsx"):
        """
        Fetches and initializes the price of the underlying asset.

        Raises:
            Exception: Specific error message described in underlying_asset.py
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        df_underlying = pd.read_excel(file_path)

        required_columns = ["Security Label", "Ticker", "ISIN", "Is Index", "Last Price"]
        missing_columns = [col for col in required_columns if col not in df_underlying.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        asset_info = df_underlying[df_underlying["Security Label"] == self.underlying_asset.name]
        if asset_info.empty:
            raise ValueError(f"No data found for security name: {self.underlying_asset.name}")
        
        self.underlying_asset.load_underlying_info(asset_info)

    def _fetch_volatility_surface(self):
        """
        Feteches and format implied volatility data to prepare the volatility surface calibration.
        """
        # Check for file existence
        if not os.path.exists(f"data/option_data/option_data_{self.underlying_asset.ticker}.xlsx"):
            raise FileNotFoundError(f"'data/option_data/option_data_{self.underlying_asset.ticker}.xlsx' does not exist.")
        else:
            option_data = pd.read_excel(f"data/option_data/option_data_{self.underlying_asset.ticker}.xlsx")

        # Convert long format to short format
        option_data = pd.melt(option_data, id_vars=['Maturity'], var_name='Strike', value_name='Implied Volatility')

        # Check for mandatory columns
        required_columns = ["Maturity", "Implied Volatility", "Strike"]
        missing_columns = [col for col in required_columns if col not in option_data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convertions
        option_data['Implied Volatility'] = option_data['Implied Volatility'].astype(float)
        option_data['Strike'] = option_data['Strike'].astype(float)
        option_data["Maturity"] = option_data["Maturity"].apply(self._convert_maturities)
        option_data["Spot"] = self.underlying_asset.last_price
        
        # Calibrate the rate curve if not done yet
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
        return self.rate_curve.get_rate(maturity) / 100
    
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
