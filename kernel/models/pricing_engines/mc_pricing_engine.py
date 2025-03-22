from .abstract_pricing_engine import AbstractPricingEngine
from ..discritization_schemes.abstract_sheme import AbstractScheme
from ..discritization_schemes.path_independent_scheme import PathIndependentScheme
from ..stochastic_processes.stochastic_process import StochasticProcess
from ..stochastic_processes.black_scholes_process import BlackScholesProcess
from kernel.products.options.abstract_option import AbstractOption
from kernel.market_data.market import Market
import numpy as np


class MCPricingEngine(AbstractPricingEngine):
    """
    A Monte Carlo pricing engine for path independent financial derivatives.

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """

    def __init__(self, n_paths: float, market: Market):
        """
        Initializes the pricing engine.

        Parameters:
            n_paths (float): The number of paths to simulate
            market (Market): The market data used for pricing
            scheme (AbstractScheme): The discretization scheme used for simulation
        """
        super().__init__(market)
        self.n_paths = n_paths

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
        
        return BlackScholesProcess(S0=initial_value, T=T, nb_steps=1, drift=drift, volatility=volatility)

    def compute_price(self, derivative: AbstractOption) -> float:
        """
        Computes the price of a path independent derivative using the Monte Carlo simulation.

        Parameters:
            derivative (AbstractOption): The derivative to price.

        Returns:
            float: The computed price of the derivative.
        """
        # Define the stochastic process
        self.process = self._define_process(derivative)

        # Define the scheme used for the discretization
        self.scheme = PathIndependentScheme(self.process, nb_paths=self.n_paths)
        
        # Simulate paths and compute the price
        terminal_values = self.scheme.simulate_paths()
        payoffs = np.array([derivative.payoff(value) for value in terminal_values])

        return np.mean(payoffs) * np.exp(-self.process.drift * self.process.T)
    

    def compute_greeks(self, derivative: AbstractOption, epsilon: float = 1e-4) -> dict:
        """
        Computes the greeks of the derivative using the Monte Carlo simulation and finite differences.

        Parameters:
            derivative (AbstractOption): The derivative to compute greeks for.
            epsilon (float): The small change used for finite difference calculations.

        Returns:
            dict: A dictionary containing the computed greeks.
        """
        greeks = {}

        # Compute Delta
        original_price = self.compute_price(derivative)
        self.market.underlying_asset.last_price += epsilon
        bumped_price = self.compute_price(derivative)
        self.market.underlying_asset.last_price -= epsilon
        greeks['Delta'] = (bumped_price - original_price) / epsilon

        # Compute Gamma
        self.market.underlying_asset.last_price += 2 * epsilon
        bumped_price_2 = self.compute_price(derivative)
        self.market.underlying_asset.last_price -= 2 * epsilon
        greeks['Gamma'] = (bumped_price_2 - 2 * bumped_price + original_price) / (epsilon ** 2)

        # Compute Vega
        original_volatility = self.market.get_volatility(derivative.strike, derivative.maturity*252)
        original_volatility += epsilon
        bumped_price_vol = self.compute_price(derivative)
        original_volatility = original_volatility
        greeks['Vega'] = (bumped_price_vol - original_price) / epsilon

        # Compute Theta
        original_maturity = derivative.maturity
        derivative.maturity -= epsilon
        bumped_price_theta = self.compute_price(derivative)
        derivative.maturity = original_maturity
        greeks['Theta'] = (bumped_price_theta - original_price) / epsilon

        # Compute Rho
        original_rate = self.market.get_rate(derivative.maturity)
        original_rate += epsilon
        bumped_price_rho = self.compute_price(derivative)
        original_rate = original_rate
        greeks['Rho'] = (bumped_price_rho - original_price) / epsilon

        return greeks
