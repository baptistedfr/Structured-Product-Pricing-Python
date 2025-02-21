from enum import Enum
from typing import Dict
import pandas as pd

class RateCurveTypes(Enum):
    # Risk free rate yield curves
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


class Market:

    def __init__(self):
        self.rate_curves = self._fetch_yield_curves()

    def _fetch_yield_curves(self) -> Dict[str, pd.DataFrame]:
        ...