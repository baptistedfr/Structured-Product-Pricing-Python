from abc import ABC, abstractmethod
from kernel.market_data.market import Market

class AbstractPricingEngine(ABC):
    """
    Abstract base class for pricing engines.
    """
    def __init__(self, market: Market):
        self.market = market

    @abstractmethod
    def compute_price(self):
        """
        Abstract method to compute the price of the financial product.
        """
        pass

    @abstractmethod
    def compute_greeks(self):
        """
        Abstract method to compute the Greeks of the financial product.
        """
        pass

class AbstractPricingEngineBis(ABC):
    """
    Abstract base class for pricing engines.
    """
    def __init__(self, market: Market):
        self.market = market

    @abstractmethod
    def get_results(self):
        """
        Abstract method to compute the price of the financial product.
        """
        pass
