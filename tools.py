from enum import Enum
from Kernel.market_data.rate_curve.interpolators import *
# from kernel.market_data.volatility_surface import *
from Kernel.models.discritization_schemes import EulerScheme, HestonEulerScheme


class InterpolationType(Enum):
    LINEAR = LinearInterpolator
    CUBIC = CubicInterpolator
    NELSON_SIEGEL = NelsonSiegelInterpolator
    SVENSSON = SvenssonInterpolator


class RateCurveType(Enum):
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


# class VolatilitySurfaceType(Enum):
#     LOCAL = SVIVolatilitySurface
#     SVI = LocalVolatilitySurface


class CalendarConvention(Enum):

    ACT_360 = "Actual/360"
    ACT_365 = "Actual/365"
    ACT_ACT = "Actual/Actual"
    THIRTY_360 = "30/360"


class EulerSchemeType(Enum):
    """
    Enum class representing the different types of Euler schemes.
    """
    EULER = EulerScheme
    HESTON_EULER = HestonEulerScheme