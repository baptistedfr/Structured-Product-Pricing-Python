from .abstract_pricing_engine import AbstractPricingEngine
from ..stochastic_processes import StochasticProcess
from kernel.products.options.abstract_option import AbstractOption
from kernel.market_data.market import Market
from kernel.tools import ObservationFrequency
import numpy as np
import pandas as pd


class MCPricingEngine(AbstractPricingEngine):
    """
    A Monte Carlo pricing engine for classic financial derivatives (no barrier, no asian payoff ...)

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """

    def __init__(self, market: Market, nb_paths: float, nb_steps: float, 
                 discretization_method: 'EulerSchemeType', stochastic_process: StochasticProcess): # type: ignore
        """
        Initializes the pricing engine.

        Parameters:
            market (Market): The market data used for pricing
            nb_paths (float): The number of paths to simulate
            nb_steps (float): The number of steps to simulate for each path
            discretization_type (EulerSchemeType): The type of discretization scheme to use. Default is EulerSchemeType.EULER
        """
        super().__init__(market)
        self.nb_paths = nb_paths
        self.nb_steps = nb_steps
        self.discretization_method = discretization_method
        self.process = stochastic_process

    def compute_price(self, derivative: AbstractOption, obs_frequency: ObservationFrequency = ObservationFrequency.ANNUAL) -> float:
        """
        Computes the price of a derivative using the Monte Carlo simulation.

        Parameters:
            derivative (AbstractOption): The derivative to price.

        Returns:
            float: The computed price of the derivative.
        """

        # Define the scheme used for the discretization
        self.scheme = self.discretization_method.value(self.process, nb_paths=self.nb_paths)
        
        # Simulate paths and compute the payoff
        price_paths, _ = self.scheme.simulate_paths()

        # # Logique autocallable
        # payoffs = []
        # t_call = []
        # for path in price_paths:

        #     payoff, t_call = derivative.payoff(path)
        
        # total_payoff = []
        # for p, t in zip(payoffs, t_call):
        #     total_payoff.append(p * np.exp(-self.process.drift * t))
        
        # return np.mean(total_payoff)
    
        payoffs = np.array([derivative.payoff(path) for path in price_paths])

        return np.mean(payoffs) * np.exp(-self.process.drift * self.process.T)
    
    # Mapping discrztization : annuel / semi annuel

    # def compute_coupon():
    #     dichotomy
    #     while : compute_price
            
    def compute_greeks(self, derivative: AbstractOption, epsilon: float = 1e-3) -> pd.DataFrame:
        """
        Computes the greeks of the derivative using the Monte Carlo simulation and finite differences.

        Parameters:
            derivative (AbstractOption): The derivative to compute greeks for.
            epsilon (float): The small change used for finite difference calculations.

        Returns:
            pd.DataFrame: A DataFrame containing the computed greeks.
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

        return pd.DataFrame([greeks], index=["Greeks"])

    def plot_paths(self, derivative: AbstractOption, nb_paths_plot: int = 100, plot_variance: bool = False):
        """
        Plots the simulated paths of the stochastic process.

        Parameters:
            derivative (AbstractOption): The derivative to plot paths for.
        """
        # Set temporary number of paths for plotting
        nb_path_origin = self.nb_paths
        self.nb_paths = nb_paths_plot

        self.scheme = self.discretization_method.value(self.process, nb_paths=self.nb_paths)
        self.scheme.plot_paths(nb_paths_plot, plot_variance)

        # Reset the number of paths
        self.nb_paths = nb_path_origin