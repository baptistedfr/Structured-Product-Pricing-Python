from abc import ABC, abstractmethod
from kernel.market_data.market import Market
from kernel.products.abstract_derive import AbstractDerive
from utils.pricing_results import PricingResults
from kernel.models.stochastic_processes import StochasticProcess

class AbstractPricingEngine(ABC):
    """
    Abstract base class for pricing engines.
    """
    def __init__(self, market: Market):
        self.market = market

    @abstractmethod
    def get_results(self,derivative:AbstractDerive) -> 'PricingResults':
        """
        Abstract method to compute the pricing results of the financial product.
        """
        pass

    @abstractmethod
    def _get_price(self, derivative: AbstractDerive,stochastic_process : StochasticProcess) -> float:
        """
        Abstract method to compute the price of the financial product.
        """
        pass
