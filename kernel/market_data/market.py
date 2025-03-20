from typing import Dict, List, Union
import pandas as pd
from tools import CalendarConvention, InterpolationType, RateCurveTypes
from kernel.market_data.rate_curve.rate_curve import RateCurve


class Market:

    def __init__(self, securities_tickers: Union[str, List[str]],
                 interpolation_type: InterpolationType = InterpolationType.CUBIC,
                 calendar_convention: CalendarConvention = CalendarConvention.ACT_360):
        self.interpolation_type = interpolation_type
        self.calendar_convention = calendar_convention
        self.rate_curves = self._fetch_yield_curves()
        self.securities_data = self._fetch_securities_data()

    def _fetch_yield_curves(self) -> Dict[str, RateCurve]:
        loaded_curves = {}
        for rate_curve_type in RateCurveTypes:
            try:
                data_curve = pd.read_excel(f"data/yield_curves/{rate_curve_type.value}")
                rate_curve = RateCurve(data_curve=data_curve,
                                       curve_type= str(rate_curve_type.name),
                                       interpolation_type=self.interpolation_type)
                loaded_curves[rate_curve_type.name] = rate_curve
            except:
                pass
        return loaded_curves

    def _fetch_securities_data(self):
        ...
