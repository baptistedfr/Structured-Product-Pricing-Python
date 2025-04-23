from abc import ABC, abstractmethod
from kernel.market_data.rate_curve_data.rate_curve import RateCurve
import datetime
from kernel.tools import CalendarConvention
from kernel.products.abstract_derive import AbstractDerive
from typing import Tuple

class AbstractRateProduct(AbstractDerive):
    def __init__(self, notional: float, emission: datetime, maturity: datetime, calendar_convention: CalendarConvention = None, frequency: int = None):
        self.notional = notional
        self.start = emission
        self.end = maturity
        self.date = None
        self.frequency = frequency if frequency is None else frequency.value
        self.convention = calendar_convention.value

    @abstractmethod
    def calculate(self,valuation_date:datetime) -> Tuple[float, float]:
        """
        Calculate the price and the market rate of the rate product.
        """
        pass

    def payoff(self) -> float:
        pass