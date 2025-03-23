import pandas as pd
import numpy as np
from scipy.stats import norm
from tools import InterpolationType
from Kernel.market_data.volatility_surface import LocalVolatilitySurface, SVIVolatilitySurface
from Kernel.market_data.rate_curve.rate_curve import RateCurve

# Get market data
spot = 230
option_data = pd.read_excel("data/option_data/option_data_old.xlsx")
option_data["Spot"] = spot
rate_data = pd.read_excel("data/yield_curves/RateCurve_temp.xlsx")

# Instantiate a rate curve
curve = RateCurve(rate_data, InterpolationType.SVENSSON)
curve.display_curve()

# Fonction de Black-Scholes
def black_scholes(S, K, T, sigma, option_type="call"):
    """
    Calcule le prix d'une option européenne avec le modèle Black-Scholes.

    :param S: Prix actuel du sous-jacent
    :param K: Strike (prix d'exercice)
    :param T: Temps jusqu'à l'expiration en années
    :param sigma: Volatilité implicite
    :param option_type: "call" ou "put"
    :return: Prix de l'option
    """
    r = curve.get_rate(T)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # Put
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return price

# Paramètres de marché
S = 220  # Prix actuel du sous-jacent (à ajuster selon le marché)
r = 0.05  # Taux sans risque (ex: 5%)
T_conversion = 365  # Convertir la maturité en années

# Convertir la volatilité implicite en float (et la maturité en années)
option_data["Implied vol"] = option_data["Implied vol"].astype(float)
option_data["Maturity"] = option_data["Maturity"].astype(float) / T_conversion

# Calculer le prix des options
option_data["Price"] = option_data.apply(lambda row: black_scholes(S, row["Strike"], row["Maturity"], row["Implied vol"], row["Type"]),
                       axis=1)

# Instantiate and calibrate a rate curve
svi = SVIVolatilitySurface(option_data=option_data, rate_curve=curve)
svi.calibrate_surface()
print(svi.get_volatility(strike=200, maturity=20))

# Instantiate and calibrate a rate curve
lv = LocalVolatilitySurface(option_data=option_data)
lv.calibrate_surface()
print(lv.get_volatility(strike=200, maturity=100))