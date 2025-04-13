import numpy as np
from scipy.optimize import brentq
from kernel.products.taux.abstract_produits_taux import AbstractRateProduct
from kernel.market_data import Market
from kernel.tools import CalendarConvention
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


class CouponBond(AbstractRateProduct):

    def __init__(self, notional: float, emission: datetime, maturity: datetime, buying_date: datetime, coupon_rate: float, frequency: int, calendar_convention: CalendarConvention, price: float = None, ytm: float = None):
        if (price is None) and (ytm is None):
            raise ValueError('You must provide either ytm or the price')
        else:
            super().__init__(notional, emission, maturity, buying_date, calendar_convention, frequency)
            self.coupon_rate = coupon_rate
            self.intervalle = 12/self.frequency
            self.coupons= self.date_coupons()
            if price is None:
                self.ytm = ytm 
                self.price = self.present_value(self.ytm)  
            if ytm is None:
                self.price = price
                self.ytm = self.compute_ytm()
            self.test = 0
        
    def present_value(self, ytm):
        future_coupons = [c for c in self.coupons if c > self.date]
        times = np.array([(1 - self.accrued_interest()) + i / self.frequency for i in range(len(future_coupons))])
        pv_coupons = sum((self.coupon_rate * self.notional) / (1 + ytm) ** t for t in times)
        pv_principal = self.notional / (1 + ytm) ** times[-1] if times.size > 0 else 0
        return pv_coupons + pv_principal

    def compute_ytm(self):
        func = lambda ytm: self.present_value(ytm) - self.price
        ytm = brentq(func, -0.5, 1.0)
        return ytm

    def date_coupons(self):
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
    
    def price_product(self):
        return self

            




