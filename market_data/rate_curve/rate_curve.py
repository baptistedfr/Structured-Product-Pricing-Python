from typing import Union, List
import re
import numpy as np
import pandas as pd
from tools import InterpolationType

class RateCurve:

    def __init__(self, data_curve : pd.DataFrame, interpolation_type: InterpolationType = InterpolationType.NELSON_SIEGEL):
        maturities, rates = self._process_data_curve(data_curve)
        self.interpolator = interpolation_type.value(maturities, rates)

    def _process_data_curve(self, df_curve: pd.DataFrame):

        if "Pillar" not in df_curve.columns or "Rate" not in df_curve.columns:
            raise Exception(f"No Pillar or Rate column in  data !")

        df_curve["Years"] = df_curve["Pillar"].apply(self._convert_maturities)

        return np.array(df_curve["Years"]), np.array(df_curve["Rate"])

    @staticmethod
    def _convert_maturities(maturity):
        match = re.match(r"(\d+)([MWY])", maturity)
        if not match:
            raise ValueError(f"Invalid maturity : {maturity}")

        value, unit = int(match.group(1)), match.group(2)

        if unit == "W":
            return value / 52
        elif unit == "M":
            return value / 12
        elif unit == "Y":
            return value
        else:
            raise ValueError(f"Unrecognized unit : {unit}")

    def get_rate(self, maturity):
        return self.interpolator.interpolate(maturity)

    def get_discount_factor(self, maturity):
        rate = self.get_rate(maturity)
        return np.exp(-rate * maturity)
