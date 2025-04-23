import numpy as np
from scipy.optimize import brentq
from kernel.products.rate.abstract_rate_product import AbstractRateProduct
from kernel.market_data import Market
from kernel.tools import CalendarConvention
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from typing import Tuple,List

class CouponBond(AbstractRateProduct):

    def __init__(self, notional: float, emission: datetime, maturity: datetime,
                 coupon_rate: float, frequency: int,
                 calendar_convention: CalendarConvention, price: float = None, ytm: float = None):
        if (price is None) and (ytm is None):
            raise ValueError('You must provide either ytm or the price')
        else:
            super().__init__(notional, emission, maturity, calendar_convention, frequency)
            self.coupon_rate = coupon_rate
            self.intervalle = 12/self.frequency
            self.coupons= self.date_coupons()
            self.ytm = ytm 
            self.price = price
        
    def present_value(self, ytm:float)->float:
        future_coupons = [c for c in self.coupons if c > self.date]
        times = np.array([(1 - self.accrued_interest()) + i / self.frequency for i in range(len(future_coupons))])
        pv_coupons = sum((self.coupon_rate * self.notional) / (1 + ytm) ** t for t in times)
        pv_principal = self.notional / (1 + ytm) ** times[-1] if times.size > 0 else 0
        return pv_coupons + pv_principal

    def compute_ytm(self):
        func = lambda ytm: self.present_value(ytm) - self.price
        ytm = brentq(func, -0.5, 1.0)
        return ytm

    def date_coupons(self)-> List[datetime]:
        """
        Génère les dates de paiement de coupons en respectant l'intervalle de paiement.
        Ne génère aucun coupon trop proche de l'émission ou juste avant la maturité.
        """
        dates = []
        current = self.start + relativedelta(months=int(self.intervalle))
        
        while current <= self.end - relativedelta(months=int(self.intervalle)):
            dates.append(current)
            current += relativedelta(months=int(self.intervalle))

        dates.append(self.end)
        return dates

    def accrued_interest(self) -> float:
        last_coupon = max((c for c in self.coupons if c <= self.date), default=self.start) + relativedelta(days=1)
        next_coupon = min((c for c in self.coupons if c > self.date), default=self.end)
        days_since = (self.date - last_coupon).days
        total_days = (next_coupon - last_coupon).days

        if self.convention == CalendarConvention.ACT_360.value:
            total_days = 360
        elif self.convention == CalendarConvention.ACT_365.value:
            total_days = 365
        elif self.convention == CalendarConvention.THIRTY_360.value:
            d1, d2 = min(last_coupon.day, 30), min(self.date.day, 30)
            days_since = 360 * (self.date.year - last_coupon.year) + 30 * (self.date.month - last_coupon.month) + (d2 - d1)

            d2 = min(next_coupon.day, 30)
            total_days = 360 * (next_coupon.year - last_coupon.year) + 30 * (next_coupon.month - last_coupon.month) + (d2 - d1)

        elif self.convention == CalendarConvention.ACT_ACT.value:
            total_days = 366 if calendar.isleap(last_coupon.year) else 365
        else: 
            raise ValueError("Convention calendaires non existante")

        return days_since / total_days if total_days else 0
    
    def calculate(self,valuation_date:datetime)-> Tuple[float, float]:
        if valuation_date is None:
            self.date = self.start
        else:
            self.date = valuation_date

        if self.price is None:
            self.price = self.present_value(self.ytm)  
        if self.ytm is None:
            self.ytm = self.compute_ytm()
        return self.price, self.ytm
            

class ZeroCouponBond(CouponBond):
    def __init__(self, notional: float, emission: datetime, maturity: datetime,
                 calendar_convention: CalendarConvention,
                 price: float = None, ytm: float = None):
        
        super().__init__(
            notional=notional,
            emission=emission,
            maturity=maturity,
            coupon_rate=0.0,
            frequency=None,
            calendar_convention=calendar_convention,
            price=price,
            ytm=ytm
        )

        self.coupons = []  
        if self.date == self.start and self.ytm is None:
            raise ValueError("À la date d’émission, il faut fournir le YTM.")

    def present_value(self, ytm: float) -> float:
        return self.notional / ((1 + ytm) ** self.time_to_maturity)

    def accrued_interest(self) -> float:
        return 0.0  

    def calculate(self,valuation_date: datetime) -> Tuple[float, float]:
        if valuation_date is None:
            self.date = self.start
        else:
            self.date = valuation_date
        if self.price is None:
            self.price = self.present_value(self.ytm)
        elif self.ytm is None:
            self.ytm = self.compute_ytm()
        else:
            raise ValueError("Les deux valeurs (prix et ytm) sont déjà définies.")
        return self.price, self.ytm


