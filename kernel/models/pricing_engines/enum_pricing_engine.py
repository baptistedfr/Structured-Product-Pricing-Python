from enum import Enum
from .mc_pricing_engine import MCPricingEngine
from .callable_mc_pricing_engine import CallableMCPricingEngine
from .callable_mc_pricing_engine_bis import CallableMCPricingEngineBis

from .mc_pricing_engine_bis import MCPricingEngineBis

class PricingEngineType(Enum):
    MC = MCPricingEngine
    CALLABLE_MC = CallableMCPricingEngine
    MC_BIS = MCPricingEngineBis


class PricingEngineTypeBis(Enum):
    CALLABLE_MC_BIS = CallableMCPricingEngineBis
    MC_BIS = MCPricingEngineBis
