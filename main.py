import pandas as pd
from market_data.rate.rate_curve import InterpolationType
from market_data.market import Market, RateCurveTypes
import time

start = time.time()
market = Market(interpolation_type=InterpolationType.SVENSSON)
rate_interpol = market.rate_curves[str(RateCurveTypes.RF_US_TREASURY.name)].get_rate(1.2)
discount = market.rate_curves[str(RateCurveTypes.RF_US_TREASURY.name)].get_discount_factor(1.2)
print(f"{time.time()-start} sec")

print(rate_interpol)
print(discount)
print('end')