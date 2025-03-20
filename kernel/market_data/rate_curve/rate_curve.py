import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tools import InterpolationType
from typing import Tuple

class RateCurve:
    """
    Defines a yield curve model based on market data and an interpolation method.

    This class processes market rate data, interpolates missing values, and provides methods to compute yields
    and discount factors. The interpolation can be based on different models such as Svensson, Nelson-Siegel...
    """

    def __init__(self, data_curve: pd.DataFrame, interpolation_type: InterpolationType = InterpolationType.SVENSSON):
        """
        Initializes the rate curve with market data and an interpolation method.

        Parameters:
            data_curve (pd.DataFrame): Market yield data with 'Pillar' (maturity) and 'Rate' (yield) columns.
            interpolation_type (InterpolationType): The interpolation method to use for yield curve fitting.
        """
        maturities, rates = self._process_data_curve(data_curve)

        self.interpolator = interpolation_type.value(maturities, rates)
        self.data_curve = data_curve

    def _process_data_curve(self, df_curve: pd.DataFrame) -> Tuple[np.ndarray[float], np.ndarray[float]]:
        """
        Processes the input data to extract maturities and rates.
        Converts maturity formats (weeks, months, years) into year-based values.

        Parameters:
            df_curve (pd.DataFrame): Raw market data with 'Pillar' and 'Rate' columns.

        Returns:
            tuple: (maturities as np.ndarray, rates as np.ndarray)
        """
        if "Pillar" not in df_curve.columns or "Rate" not in df_curve.columns:
            raise Exception("No 'Pillar' or 'Rate' column in data!")

        df_curve["Years"] = df_curve["Pillar"].apply(self._convert_maturities)
        return np.array(df_curve["Years"]), np.array(df_curve["Rate"])

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

    def get_rate(self, maturity: float) -> float:
        """
        Retrieves the interpolated yield rate for a given maturity.

        Parameters:
            maturity (float): Desired maturity in years.

        Returns:
            float: Interpolated yield rate.
        """
        return self.interpolator.interpolate(maturity)

    def get_discount_factor(self, maturity: float) -> float:
        """
        Computes the discount factor for a given maturity using the interpolated yield.

        Parameters:
            maturity (float): Desired maturity in years.

        Returns:
            float: Discount factor
        """
        rate = self.get_rate(maturity)
        return np.exp(-rate * maturity)

    def display_curve(self) -> None:
        """
        Plots the yield curve based on market data and the chosen interpolated yield.
        """
        maturities = np.linspace(0, 30, 500)  # Generate a smooth range of maturities
        yield_curve = np.array([self.get_rate(mat) for mat in maturities])

        plt.scatter(self.data_curve['Years'], self.data_curve['Rate'], color="crimson", label='Market yields')
        plt.plot(maturities, yield_curve, label='Interpolated yield curve', color="royalblue")
        plt.xlabel('Maturity (Years)')
        plt.ylabel('Yield')
        plt.title('Implied Yield Curve & Market Rate Points')
        plt.legend()
        plt.grid(True)