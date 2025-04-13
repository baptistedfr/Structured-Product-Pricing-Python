from enum import Enum
from .callable_mc_pricing_engine import CallableMCPricingEngine
from .american_mc_pricing_engine  import AmericanMCPricingEngine
from .mc_pricing_engine import MCPricingEngine
from .RatePricingEngine import RatePricingEngine

class PricingEngineType(Enum):
    CALLABLE_MC = CallableMCPricingEngine
    MC = MCPricingEngine
    AMERICAN_MC= AmericanMCPricingEngine
    TAUX = RatePricingEngine
