from .abstract_pricing_engine import AbstractPricingEngine
from ..stochastic_processes import StochasticProcess
from kernel.products.options.abstract_option import AbstractOption
from kernel.products.options_strategies.abstract_option_strategy import AbstractOptionStrategy
from kernel.market_data.market import Market
from kernel.tools import ObservationFrequency
from utils.pricing_settings import PricingSettings
from utils.pricing_results import PricingResults
from kernel.models.stochastic_processes import BlackScholesProcess,HestonProcess
from kernel.models.stochastic_processes.black_scholes_process import BlackScholesProcess
from kernel.models.discritization_schemes.euler_scheme import EulerScheme
import numpy as np
import pandas as pd

class MCPricingEngine(AbstractPricingEngine):
    """
    A Monte Carlo pricing engine for classic financial derivatives (no barrier, no asian payoff ...)

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """

    def __init__(self, market: Market, settings : PricingSettings): # type: ignore
        """
        Initializes the pricing engine.

        Parameters:
            market (Market): The market data used for pricing
            settings (PricingSettings): The settings for the pricing engine
        """
        super().__init__(market)
        self.settings = settings
        self.nb_paths = settings.nb_paths
        self.nb_steps = settings.nb_steps
        self.random_seed = settings.random_seed
        self.enable_greeks = settings.compute_greeks 
        self.valuation_date = settings.valuation_date # pas sur que ca serve 
        self.model = settings.model


    def get_results(self, derivative: AbstractOption) -> PricingResults:
        self.derivative = derivative
        if(isinstance(derivative, AbstractOptionStrategy)):
            #if its an abstract option strategy, its a list of abstract options
            strat_results = []
            for opt,is_long in derivative.options:
                position = 1 if is_long else -1
                self._set_stochastic_process(opt)
                result = self.get_result(opt,position)
                strat_results.append(result)
            return PricingResults.get_aggregated_results(strat_results)
        else:
            #if its a single abstract option, we just call the get_result method
            return self.get_result(derivative)


    def get_result(self, derivative: AbstractOption,position : int = 1) -> PricingResults:
        """
        Returns the results of the pricing engine.

        Parameters:
            derivative (AbstractOption): The derivative to price.

        Returns:
            dict: A dictionary containing the results of the pricing engine.
        """
        # Set the stochastic process based on the model
        self.derivative = derivative
        self._set_stochastic_process(derivative)
        price = self._get_price(derivative,self.stochastic_process)
        
        pricing_results = PricingResults()
        pricing_results.price = price * position

        return pricing_results
    
    def _set_stochastic_process(self,derivative: AbstractOption) -> None: #peut etre revoir cetté méthode pour la rendre plus générique

        T = derivative.maturity
        if hasattr(derivative, "strike"):
            K = derivative.strike
        else:
            # Case when the product has no strike, for exemple autocallable products
            K = self.market.underlying_asset.last_price

        # Market parameters
        initial_value = self.market.underlying_asset.last_price
        delta_t = T / self.nb_steps
        drift = [self.market.get_rate(T) if self.nb_steps == 1 
        else self.market.get_fwd_rate(i * delta_t, (i + 1) * delta_t) for i in range(self.nb_steps)]

        volatility = self.market.get_volatility(K, T)
        
        if self.model.name == "BLACK_SCHOLES":
            self.stochastic_process= BlackScholesProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, volatility=volatility)
        elif self.model.name == "HESTON": # to do 
            theta = volatility**2
            kappa = 1
            ksi = 0.1
            rho = -0.5
            self.stochastic_process = HestonProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, theta=theta, kappa=kappa, ksi=ksi, rho=rho)

    def _get_price(self, derivative: AbstractOption,stochastic_process: StochasticProcess) -> float:
        #le paramètre process servira probablement pour les grecs
        scheme = EulerScheme()
        price_paths=scheme.simulate_paths(process=stochastic_process, nb_paths=self.nb_paths, seed=self.random_seed)
        payoffs = np.array([derivative.payoff(path) for path in price_paths])
        price = np.mean(payoffs) * self.market.get_discount_factor(derivative.maturity)
        return price


    def get_price(self):
        pass

    def compute_greeks(self):
        pass
    """
    def compute_price(self, derivative: AbstractOption, obs_frequency: ObservationFrequency = ObservationFrequency.ANNUAL) -> float:
        
        Computes the price of a derivative using the Monte Carlo simulation.

        Parameters:
            derivative (AbstractOption): The derivative to price.

        Returns:
            float: The computed price of the derivative.
        
        # Define the scheme used for the discretization
        self.scheme = self.discretization_method.value(self.process, nb_paths=self.nb_paths)
        
        # Simulate paths and compute the payoff
        price_paths, _ = self.scheme.simulate_paths()
        payoffs = np.array([derivative.payoff(path) for path in price_paths])

    """
    
        