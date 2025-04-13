from kernel.tools import CalendarConvention, ObservationFrequency, Model
from kernel.market_data import InterpolationType, VolatilitySurfaceType, Market, RateCurveType
from kernel.products.taux.Bonds import CouponBond
from kernel.products.taux.ZC import ZeroCouponBond
from kernel.products.taux.Swap import InterestRateSwap
from kernel.products.options.vanilla_options import EuropeanCallOption
from kernel.products.structured_products.autocall_products import Phoenix
from kernel.products.options_strategies.options_strategies import *
from kernel.models import MCPricingEngine, PricingEngineType
from kernel.models.discritization_schemes.euler_scheme import EulerScheme
from kernel.models.pricing_engines.enum_pricing_engine import PricingEngineType
from kernel.pricing_launcher import PricingLauncher
from utils.pricing_settings import PricingSettings
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
'''
security = "SPX"
rate_curve_type = RateCurveType.RF_US_TREASURY
interpolation_type = InterpolationType.SVENSSON
volatility_surface_type = VolatilitySurfaceType.SVI
day_count_convention = CalendarConvention.ACT_360
scheme = EulerScheme
obs_frequency = ObservationFrequency.ANNUAL
pricer_type = PricingEngineType.MC
model = Model.BLACK_SCHOLES


settings_dict = {
    "underlying_name": security,
    "rate_curve_type": rate_curve_type,
    "interpolation_type": interpolation_type,
    "volatility_surface_type": volatility_surface_type,
    "obs_frequency": obs_frequency,
    "day_count_convention": day_count_convention,
    "model": model,
    "pricing_engine_type": pricer_type,
    "nb_paths": 25000,
    "nb_steps": 400,
    "random_seed": 4012,
    "compute_greeks": False,
}
settings = PricingSettings(**settings_dict)

autocall = Phoenix(maturity=3, 
                   observation_frequency=ObservationFrequency.ANNUAL, 
                   capital_barrier=60, 
                   autocall_barrier=100, 
                   coupon_barrier=80, 
                   coupon_rate=5.0)

settings.pricing_engine_type = PricingEngineType.MC
new_launcher_autocall = PricingLauncher(pricing_settings = settings)
test = new_launcher_autocall.get_results(autocall)
print(test.price)

settings.compute_callable_coupons = True
test_coupon = new_launcher_autocall.get_results(autocall)
print(test_coupon.coupon_callable)
'''


security = "SPX"
rate_curve_type = RateCurveType.RF_US_TREASURY
interpolation_type = InterpolationType.SVENSSON
volatility_surface_type = None
day_count_convention = CalendarConvention.ACT_360
scheme = EulerScheme
obs_frequency = ObservationFrequency.ANNUAL
pricer_type = PricingEngineType.TAUX


settings_dict = {
    "underlying_name": security,
    "rate_curve_type": rate_curve_type,
    "interpolation_type": interpolation_type,
    "volatility_surface_type": VolatilitySurfaceType.SVI,
    "obs_frequency": obs_frequency,
    "day_count_convention": day_count_convention,
    "model": None,
    "pricing_engine_type": pricer_type,
    "nb_paths": None,
    "nb_steps": None,
    "random_seed": 4012,
    "compute_greeks": False,
}
settings = PricingSettings(**settings_dict)

#Pour connaitre le ytm
bond = CouponBond(notional=100,
                  emission=datetime(2024, 1, 1), 
                  maturity=datetime(2025, 1, 1),
                  buying_date = None, 
                  coupon_rate=0.02, 
                  frequency = ObservationFrequency.ANNUAL,
                  calendar_convention=day_count_convention, 
                  price=100, 
                  ytm=None
                  )

settings.pricing_engine_type = PricingEngineType.TAUX
new_launcher_bond = PricingLauncher(pricing_settings = settings)
test = new_launcher_bond.get_results(bond)
print(test.ytm)

#Pour connaitre le prix à une date t (c'est le dirty price)
bond = CouponBond(notional=100,
                  emission=datetime(2024, 1, 1), 
                  maturity=datetime(2027, 1, 1),
                  buying_date = datetime(2025, 1, 1), 
                  coupon_rate=0.02, 
                  frequency = ObservationFrequency.SEMIANNUAL,
                  calendar_convention=day_count_convention, 
                  price=None, 
                  ytm=0.04
                  )

settings.pricing_engine_type = PricingEngineType.TAUX
new_launcher_bond = PricingLauncher(pricing_settings = settings)
test = new_launcher_bond.get_results(bond)
print(test.price)

# A t=0 pour connaitre le juste taux fixe
new_launcher_swap = PricingLauncher(pricing_settings = settings)
new_launcher_swap._init_market()
swap = InterestRateSwap(notional=100,
                        emission=datetime(2015,1,1), 
                        maturity=datetime(2025,1,1), 
                        buying_date=None,
                        calendar_convention=day_count_convention,
                        fixed_rate=None, 
                        float_spread=0.0,
                        frequency=ObservationFrequency.ANNUAL,
                        price=None,
                        curve= new_launcher_swap.market.rate_curve
                        )

test = new_launcher_swap.get_results(swap)
print(test.fixed_rate)

#En t = X pour connaitre la valeur du swap
new_launcher_swap = PricingLauncher(pricing_settings = settings)
new_launcher_swap._init_market()
swap = InterestRateSwap(notional=100,
                        emission=datetime(2015,1,1), 
                        maturity=datetime(2025,1,1), 
                        buying_date=datetime(2017,1,1),
                        calendar_convention=day_count_convention,
                        fixed_rate=0.02, 
                        float_spread=0.0,
                        frequency=ObservationFrequency.ANNUAL,
                        price=None,
                        curve= new_launcher_swap.market.rate_curve
                        )

test = new_launcher_swap.get_results(swap)
print(test.price)

new_launcher_ZC = PricingLauncher(pricing_settings = settings)
zc = ZeroCouponBond(notional=100,
                      emission=datetime(2015,1,1), 
                      maturity=datetime(2025,1,1), 
                      buying_date=(2017,1,1),
                      calendar_convention=day_count_convention,
                      market_price=90,
                      ytm=None)

test = new_launcher_swap.get_results(zc)
print(test.ytm)



