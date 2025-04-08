from datetime import datetime
from typing import Optional
#from kernel.models.pricing_engines.enum_pricing_engine import PricingEngineTypeBis
from kernel.tools import *
from kernel.market_data import InterpolationType, VolatilitySurfaceType

class PricingSettings:
    def __init__(self): #a voir si on fait tout saisir à l'utilisateur ou pas 
        self.day_count_convention: Optional[str] = None
        self.nb_paths: Optional[int] = None
        self.nb_steps: Optional[int] = None
        self.valuation_date: Optional[datetime] = None
        self.compute_greeks: bool = False
        self.random_seed: Optional[int] = 4012
        self.model: Optional[Model] = None  # a voir
        self.rate_curve_type: Optional[RateCurveType] = None
        self.interpolation_type: Optional[InterpolationType] = None
        self.volatility_surface_type: Optional[VolatilitySurfaceType] = None
        self.obs_frequency: Optional[ObservationFrequency] = ObservationFrequency.ANNUAL
        self.pricing_engine_type = None
        self.underlying_name: Optional[str] = None
        self.compute_callable_coupons = False

