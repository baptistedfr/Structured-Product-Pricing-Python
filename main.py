import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from market_data.volatility_surface.svi_volatility import SVIVolatilitySurface

spot = 230

option_data = pd.read_csv("data/option_data.csv", sep=",")
option_data["Spot"] = spot
option_data = option_data[option_data["Maturity"] == 24]
print(option_data.head())

svi = SVIVolatilitySurface(option_data)
svi.calibrate_surface()
svi.svi_params = [-2.99248987e+00,  4.46937635e+01, -1.09724879e-01,  1.04154911e-02, 9.54917171e-02]
