
import numpy as np
from scipy.optimize import brentq
from kernel.products.rate.abstract_rate_product import AbstractRateProduct
from kernel.market_data import Market
from kernel.tools import CalendarConvention
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.day_counter import DayCounter
from typing import Tuple, List  

class InterestRateSwap(AbstractRateProduct):

    def __init__(self, notional: float, emission: datetime, maturity: datetime, calendar_convention: CalendarConvention = None,
                 fixed_rate: float = None, float_spread: float=0.0, frequency: int = 1,
                 price: float = None):
        
        super().__init__(notional, emission, maturity, calendar_convention, frequency)
        self.float_spread=float_spread
        self.interval = 12 / self.frequency
        self.day_counter = DayCounter(self.convention)
        self.fixed_rate = fixed_rate
        self.price = price

    def set_market(self, market: Market):
        self.market = market

    def generate_payment_dates(self, interval:float)-> List[datetime]:
        dates = []
        current = self.start + relativedelta(months=int(interval))
        while current < self.end:
            dates.append(current)
            current += relativedelta(months=int(interval))
        dates.append(self.end)
        return [d for d in dates if d > self.date]

    def present_value(self)-> float:
        if(self.date == self.start):
            return 0.0
        fixed_leg_pv = self.fixed_leg_value()
        float_leg_pv = self.float_leg_value()
        return float_leg_pv - fixed_leg_pv

    def get_annuities(self)-> float:
        annuities = 0
        prev_date = self.start
        for d in self.dates:
            if d > self.date:
                yf = self.day_counter.get_year_fraction(prev_date, d)
                t = (d - self.date).days / 365
                df = self.market.get_discount_factor(t)
                annuities += yf * df
                prev_date = d
        return annuities
    
    def fixed_leg_value(self)-> float:
        return self.fixed_rate * self.notional * self.get_annuities()
    
    def float_leg_value(self)-> float:
        pv = 0
        prev_date = self.start
        for d in self.dates:
            if d > self.date:
                t1 = (prev_date - self.date).days / 365
                t2 = (d - self.date).days / 365
                yf = self.day_counter.get_year_fraction(prev_date, d)

                if t1 <= 0:
                    forward_rate = self.market.get_rate(t2) / 100
                else:
                    forward_rate = self.market.get_fwd_rate(t1, t2)

                forward_rate += self.float_spread / 10000.0
                df = self.market.get_discount_factor(t2)
                cashflow = self.notional * forward_rate * yf
                pv += cashflow * df
                prev_date = d
        return pv


    def par_rate(self) -> float:
        annuities = self.get_annuities()
        if annuities == 0:
            raise ZeroDivisionError("Annuities égales à 0, par rate indéterminé")

        return self.float_leg_value() / (self.notional * annuities)
    


    
    def calculate(self,valuation_date:datetime)-> Tuple[float, float]:
        if valuation_date is None:
            self.date = self.start
        else:
            self.date = valuation_date

        self.dates = self.generate_payment_dates(self.interval)
        if self.fixed_rate is None:
            self.fixed_rate = self.par_rate()
        if self.price is None:
            self.price = self.present_value()
        return self.price, self.fixed_rate





