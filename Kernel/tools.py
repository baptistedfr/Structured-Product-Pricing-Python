from enum import Enum

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

class CalendarConvention(Enum):

    ACT_360 = "Actual/360"
    ACT_365 = "Actual/365"
    ACT_ACT = "Actual/Actual"
    THIRTY_360 = "30/360"

class ObservationFrequency(Enum):
    """
    Enum mapping observation frequencies to the number of periods in a year.
    """
    ANNUAL = 1          # Annuel
    SEMIANNUAL = 2      # Semi-annuel
    QUARTERLY = 4       # Trimestriel
    MONTHLY = 12        # Mensuel