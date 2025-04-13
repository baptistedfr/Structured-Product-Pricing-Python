from kernel.tools import CalendarConvention
import calendar
import datetime 
from scipy.optimize import brentq
from kernel.products.taux.abstract_produits_taux import AbstractRateProduct

class ZeroCouponBond(AbstractRateProduct):

    def __init__(self, notional: float, emission: datetime, maturity: datetime, buying_date: datetime,calendar_convention: CalendarConvention=None, market_price: float = None, ytm: float = None):
        super().__init__(notional, emission, maturity, buying_date, calendar_convention)

        self.time_to_maturity = self._year_fraction(self.date, self.end)

        if market_price is None and ytm is None:
            raise ValueError('You must provide either ytm or the price')
        if self.date == self.start and self.ytm is None:
            raise ValueError('A date d émission, il faut fournir un ytm')
        if ytm is None:
            self.price = market_price
            self.ytm = self.yield_to_maturity()
        if market_price is None:
            self.ytm = ytm
            self.price = self.present_value(ytm)


    def present_value(self, ytm: float) -> float:
        return self.notional / ((1 + ytm) ** self.time_to_maturity)

    def yield_to_maturity(self) -> float:
        return (self.notional / self.price) ** (1 / self.time_to_maturity) - 1

    def _year_fraction(self, start: datetime, end: datetime) -> float:
        days = (self.end - self.start).days
        if self.convention == CalendarConvention.ACT_365.value:
            return days / 365.0

        elif self.convention == CalendarConvention.ACT_360.value:
            return days / 360.0

        elif self.convention == CalendarConvention.THIRTY_360.value:
            d1 = min(start.day, 30)
            d2 = min(end.day, 30)
            total_days = 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)
            return total_days / 360.0

        elif self.convention == CalendarConvention.ACT_ACT.value:
            year_length = 365.25 
            return days / year_length

        else:
            raise ValueError(f"Unsupported convention: {self.convention}")

    def price_product(self):
        return self