from kernel.tools import CalendarConvention, ObservationFrequency, Model
from kernel.market_data import InterpolationType, VolatilitySurfaceType, Market, RateCurveType

from kernel.products.options.vanilla_options import EuropeanCallOption
from kernel.products.structured_products.autocall_products import Phoenix
from kernel.products.options_strategies.options_strategies import *
from kernel.models import MCPricingEngine, EulerSchemeType, PricingEngineType
from kernel.models.pricing_engines.enum_pricing_engine import PricingEngineTypeBis
from kernel.pricing_launcher import PricingLauncher
from kernel.pricing_launcher_bis import PricingLauncherBis
from utils.pricing_settings import PricingSettings
import numpy as np
import pandas as pd
from scipy.stats import norm

security = "SPX"
rate_curve_type = RateCurveType.RF_US_TREASURY
interpolation_type = InterpolationType.SVENSSON
volatility_surface_type = VolatilitySurfaceType.SVI
day_count_convention = CalendarConvention.ACT_360
scheme = EulerSchemeType.EULER
obs_frequency = ObservationFrequency.ANNUAL
pricer_type = PricingEngineType.MC_BIS
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

settings.pricing_engine_type = PricingEngineTypeBis.CALLABLE_MC_BIS
new_launcher_autocall = PricingLauncherBis(pricing_settings = settings)
test = new_launcher_autocall.get_results(autocall)
print(test.price)

settings.compute_callable_coupons = True
test_coupon = new_launcher_autocall.get_results(autocall)
print(test_coupon.coupon_callable)