import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tools import InterpolationType
from market_data.volatility_surface.svi_volatility import SVIVolatilitySurface
from market_data.rate_curve.rate_curve import RateCurve

# Get market data
spot = 230
option_data = pd.read_excel("data/option_data.xlsx")
option_data["Spot"] = spot
rate_data = pd.read_excel("data/yield_curves/RateCurve_temp.xlsx")

# Instantiate a rate curve
curve = RateCurve(rate_data, InterpolationType.SVENSSON)

# Instantiate and calibrate a rate curve
svi = SVIVolatilitySurface(option_data=option_data, rate_curve=curve)
svi.calibrate_surface()
print(svi.get_volatility(strike=200, maturity=100))