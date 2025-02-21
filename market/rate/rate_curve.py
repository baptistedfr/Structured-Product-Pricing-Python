from enum import Enum
from market.rate.interpolator import *
from typing import Union, List

import numpy as np

class InterpolationType(Enum):
    LINEAR = LinearInterpolator
    CUBIC = CubicInterpolator
    NELSON_SIEGEL = NelsonSiegelInterpolator
    STEVENSON = StevensonInterpolator

class RateCurve:

    def __init__(self, maturities: Union[List, np.ndarray], rates: Union[List, np.ndarray], interpolation_type: InterpolationType):
        self.interpolator = interpolation_type.value(maturities, rates)

    def get_rate(self, maturity):
        return self.interpolator.interpolate(maturity)

    def get_discount_factor(self, maturity):
        rate = self.get_rate(maturity)
        return np.exp(-rate * maturity)
