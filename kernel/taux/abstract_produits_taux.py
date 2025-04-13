from abc import ABC, abstractmethod
from kernel.market_data.rate_curve_data.rate_curve import RateCurve
import datetime
from kernel.tools import CalendarConvention


class AbstractRateProduct(ABC):
    def __init__(self, notional: float, emission: datetime, maturity: datetime, buying_date: datetime, calendar_convention: CalendarConvention = None, frequency: int = None):
        self.notional = notional
        self.start = emission
        self.end = maturity
        self.date = self.start if buying_date is None else buying_date
        self.frequency = frequency.value if frequency is not None else frequency
        self.convention = calendar_convention.value

    @abstractmethod
    def present_value(self, rate_curve: RateCurve) -> float:
        pass
