
import numpy as np
from scipy.optimize import brentq
from kernel.products.taux.abstract_produits_taux import AbstractRateProduct
from kernel.market_data import Market
from kernel.tools import CalendarConvention
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from kernel.market_data.rate_curve_data import RateCurve

class InterestRateSwap(AbstractRateProduct):

    def __init__(self, notional: float, emission: datetime, maturity: datetime, buying_date: datetime = None, calendar_convention: CalendarConvention = None,
                 fixed_rate: float = None, float_spread: float=0.0, frequency: int = 1,
                 price: float = None, curve: RateCurve = None):
        
        super().__init__(notional, emission, maturity, buying_date, calendar_convention, frequency)
        self.float_spread=float_spread
        self.curve = curve
        self.interval = 12 / self.frequency
        self.dates = self.generate_payment_dates(self.interval)

        if self.date == self.start:
            self.fixed_rate = self.par_rate()
            self.price = 0.0
        else:
            if fixed_rate is None:
                raise ValueError("Le taux fixe doit être renseigné, il n'est pas")
            self.fixed_rate = fixed_rate
            self.price = self.present_value()

    def generate_payment_dates(self, interval):
        dates = []
        current = self.start + relativedelta(months=int(interval))
        while current < self.end:
            dates.append(current)
            current += relativedelta(months=int(interval))
        dates.append(self.end)
        return [d for d in dates if d > self.date]

    def discount_factor(self, t: float) -> float:
        rate = self.curve.get_rate(t) / 100
        return np.exp(-rate * t)

    def forward_rate(self, t1: float, t2: float):
        r1 = self.curve.get_rate(t1) / 100
        r2 = self.curve.get_rate(t2) / 100
        return ((1 + r2)**t2 / (1 + r1)**t1)**(1 / (t2 - t1)) - 1

    def year_fraction(self, start_date: datetime, end_date: datetime) -> float:
        if self.convention == CalendarConvention.ACT_360.value:
            return (end_date - start_date).days / 360
        elif self.convention == CalendarConvention.ACT_365.value:
            return (end_date - start_date).days / 365
        elif self.convention == CalendarConvention.THIRTY_360.value:
            d1 = min(start_date.day, 30)
            d2 = min(end_date.day, 30)
            return (360 * (end_date.year - start_date.year) +
                    30 * (end_date.month - start_date.month) +
                    (d2 - d1)) / 360
        elif self.convention == CalendarConvention.ACT_ACT.value:
            year_length = 366 if calendar.isleap(start_date.year) else 365
            return (end_date - start_date).days / year_length
        else:
            raise ValueError("Convention calendaire non reconnue.")

    def present_value(self):
        fixed_leg_pv = self.fixed_leg_value()
        float_leg_pv = self.float_leg_value()
        return float_leg_pv - fixed_leg_pv

    def fixed_leg_value(self):
        pv = 0
        prev_date = self.start
        for d in self.dates:
            if d > self.date:
                yf = self.year_fraction(prev_date, d)
                t = (d - self.date).days / 365
                df = self.discount_factor(t)
                pv += self.fixed_rate * self.notional * yf * df
                prev_date = d
        return pv

    def float_leg_value(self):
        pv = 0
        prev_date = self.start
        for d in self.dates:
            if d > self.date:
                t1 = (prev_date - self.date).days / 365
                t2 = (d - self.date).days / 365
                yf = self.year_fraction(prev_date, d)

                if t1 <= 0:
                    forward_rate = self.curve.get_rate(t2) / 100
                else:
                    forward_rate = self.forward_rate(t1, t2)

                forward_rate += self.float_spread / 10000.0
                df = self.discount_factor(t2)
                cashflow = self.notional * forward_rate * yf
                pv += cashflow * df
                prev_date = d
        return pv


    def par_rate(self, tol=1e-7):
        """Trouve le taux fixe (par rate) tel que NPV = 0, via brentq."""
        def npv_diff(fixed_rate_guess: float = 0.01):
            self.fixed_rate = fixed_rate_guess
            return self.present_value()

        return brentq(npv_diff, 0.0001, 0.20, xtol=tol)
    
    def price_product(self):
        return self

