from enum import Enum
from market_data.rate_curve.interpolators.abstract_interpolator import *

class InterpolationType(Enum):
    LINEAR = LinearInterpolator
    CUBIC = CubicInterpolator
    NELSON_SIEGEL = NelsonSiegelInterpolator
    SVENSSON = SvenssonInterpolator

class RateCurveTypes(Enum):
    # Risk free rate_curve yield curves
    RF_US_TREASURY = "RateCurve_temp.xlsx"
    RF_OAT = ""
    # Swap curves
    SWAP_EURIBOR = ""
    SWAP_SOFR = ""
    # OIS curves
    OIS_SOFR = ""
    OIS_ESTER = ""
    # Credit spread curves
    CREDIT_IG = ""
    CREDIT_HY = ""


class CalendarConvention(Enum):

    ACT_360 = "Actual/360"
    ACT_365 = "Actual/365"
    ACT_ACT = "Actual/Actual"
    THIRTY_360 = "30/360"