import pandas as pd
from market.rate.rate_curve import RateCurve, InterpolationType

rate_curve_data = pd.read_excel("RateCurve_temp.xlsx")
rate = RateCurve(maturities=rate_curve_data["Matu"],
                 rates=rate_curve_data["Rate"],
                 interpolation_type=InterpolationType.LINEAR)
rate_interpol = rate.get_rate(1.2)
print(rate_interpol)

rate = RateCurve(maturities=rate_curve_data["Matu"],
                 rates=rate_curve_data["Rate"],
                 interpolation_type=InterpolationType.CUBIC)
rate_interpol = rate.get_rate(1.2)
print(rate_interpol)