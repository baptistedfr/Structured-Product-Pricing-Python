from kernel.market_data import Market
from kernel.models.stochastic_processes import *
from kernel.models.pricing_engines.enum_pricing_engine import PricingEngineTypeBis
from kernel.products.abstract_derive import AbstractDerive
from utils.pricing_results import PricingResults
from kernel.products.structured_products import AbstractStructuredProduct
from utils.pricing_settings import PricingSettings 
from kernel.models.pricing_engines.mc_pricing_engine_bis import MCPricingEngineBis  #temp
from typing import Union


class PricingLauncherBis:
    """
    The pricing launcher defines the objects used for the pricing as follow:
        - Based on the selected diffusion (BS, Heston...) the associated stochastic process is defined
    """

    def __init__(self, pricing_settings : PricingSettings): # type: ignore

        self.settings = pricing_settings

    def _init_market(self):
        """
        Initializes the market object with the given settings.
        """
        self.market = Market(underlying_name=self.settings.underlying_name, rate_curve_type=self.settings.rate_curve_type,
                             interpolation_type=self.settings.interpolation_type, 
                             volatility_surface_type=self.settings.volatility_surface_type,
                             calendar_convention=self.settings.day_count_convention,
                             obs_frequency=self.settings.obs_frequency)

    def get_results(self,derivative: AbstractDerive) -> Union[PricingResults]:
        #a terme devrait s'appeler calculate et ca lirait les produits directement via une classe d'interface ? et afficherait les resultats ?
        """
        Main method to perform the pricing calculation.
        """
        # Initialize market
        self._init_market()

        # Initialize pricer
        engine = PricingEngineTypeBis[self.settings.pricing_engine_type.name].value(market=self.market,settings=self.settings)
        
        #engine = MCPricingEngineBis(market = self.market,settings=self.settings) #temporaire, faudra modifer les autres engines
        results = engine.get_results(derivative=derivative)
        
        return results #temporary


