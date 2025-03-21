from .abstract_pricing_engine import AbstractPricingEngine
from ..discritization_schemes.abstract_sheme import AbstractScheme
from ..discritization_schemes.euler_scheme import EulerScheme
from ..stochastic_processes.stochastic_process import StochasticProcess
from ..stochastic_processes.black_scholes_process import BlackScholesProcess
from kernel.products.options.abstract_option import AbstractOption
from kernel.market_data.market import Market
import numpy as np


class MCPricingEngine(AbstractPricingEngine):
    """
    A Monte Carlo pricing engine for financial derivatives.

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """

    def __init__(self, n_paths: float, n_steps: float, market: Market):
        """
        Initializes the pricing engine.

        Parameters:
            n_paths (float): The number of paths to simulate
            n_steps (float): The number of steps in each path
            market (Market): The market data used for pricing
            scheme (AbstractScheme): The discretization scheme used for simulation
        """
        super().__init__(market)
        self.n_paths = n_paths
        self.n_steps = n_steps

    def _define_process(self, derivative: AbstractOption) -> BlackScholesProcess:
        """
        Defines the stochastic process used for simulation based on market & derivatives parameters.

        Returns:
            BlackScholesProcess: The stochastic process used for simulation.
        """
        # Derivates parameters
        T = derivative.maturity
        K = derivative.strike

        # Market parameters
        initial_value = self.market.underlying_asset.last_price
        drift = self.market.get_rate(T) / 100
        volatility = self.market.get_volatility(K, T*252) # Corriger la maturité de jours en années dans les fichiers de vol
        
        return BlackScholesProcess(initial_value, T, self.n_steps, volatility, drift)

    def compute_price(self, derivative: AbstractOption) -> float:
        """
        Computes the price of a derivative using the Monte Carlo simulation.

        Parameters:
            derivative (AbstractDerive): The derivative to price.

        Returns:
            float: The computed price of the derivative.
        """
        # Define the stochastic process
        self.process = self._define_process(derivative)

        # Define the scheme used for the discretization
        self.scheme = EulerScheme(self.process, nb_paths=self.n_paths)
        
        # Simulate paths and compute the price
        paths = self.scheme.simulate_paths()
        payoffs = np.array([derivative.payoff(path) for path in paths])

        return np.mean(payoffs)*np.exp(-self.process.drift*self.process.T)
    

    def compute_greeks(self):
        pass