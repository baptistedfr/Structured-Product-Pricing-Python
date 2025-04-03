from enum import Enum
from .mc_pricing_engine import MCPricingEngine
from .callable_mc_pricing_engine import CallableMCPricingEngine

class PricingEngineType(Enum):
    MC = MCPricingEngine
    CALLABLE_MC = CallableMCPricingEngine