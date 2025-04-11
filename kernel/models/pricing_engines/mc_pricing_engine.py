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
                process = self.get_stochastic_process(derivative=opt,market=self.market)
                result = self.get_result(derivative=opt,position=position)
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
        process = self.get_stochastic_process(derivative=derivative,market=self.market)
        price = self._get_price(derivative,process)
        
        pricing_results = PricingResults()
        pricing_results.price = price * position

        delta= self.get_delta(derivative=derivative, epsilon=1) * position
        gamma = self.get_gamma(derivative=derivative, epsilon=1) * position
        vega = self.get_vega(derivative=derivative, epsilon=0.01) * position
        vega2 = self.get_vega2(derivative=derivative, epsilon=0.01) * position
        rho = self.get_rho(derivative=derivative, epsilon=0.0001) * position

        pricing_results.set_greek("delta", delta)
        pricing_results.set_greek("gamma", gamma)
        pricing_results.set_greek("vega", vega)
        pricing_results.set_greek("vega2", vega2)
        pricing_results.set_greek("rho", rho)
        
        return pricing_results
    
    def get_stochastic_process(self, derivative: AbstractOption, market: Market) -> StochasticProcess:
        T = derivative.maturity
        # Détermine le strike : si le produit n'en a pas, on utilise le dernier prix de l'underlying du marché
        if hasattr(derivative, "strike"):
            K = derivative.strike
        else:
            K = market.underlying_asset.last_price

        initial_value = market.underlying_asset.last_price
        delta_t = T / self.nb_steps
        drift = [
        market.get_rate(T) if self.nb_steps == 1 
        else market.get_fwd_rate(i * delta_t, (i + 1) * delta_t) for i in range(self.nb_steps)
    ]
        volatility = market.get_volatility(K, T)

        if self.model.name == "BLACK_SCHOLES":
            return BlackScholesProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, volatility=volatility)
        elif self.model.name == "HESTON":
            theta = volatility ** 2
            kappa = 1
            ksi = 0.1
            rho = -0.5
            return HestonProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, theta=theta, kappa=kappa, ksi=ksi, rho=rho)

    def _get_price(self, derivative: AbstractOption,stochastic_process: StochasticProcess) -> float:
        #le paramètre process servira probablement pour les grecs
        scheme = EulerScheme()
        price_paths=scheme.simulate_paths(process=stochastic_process, nb_paths=self.nb_paths, seed=self.random_seed)
        payoffs = np.array([derivative.payoff(path) for path in price_paths])
        price = np.mean(payoffs) * self.market.get_discount_factor(derivative.maturity)
        return price


    def get_delta(self, derivative: AbstractOption, epsilon: float = 1) -> float:
        """
        Calcule le delta du produit via différence finie centrée, sans modifier de variables d'instance.
        """
    
        process_up = self.get_stochastic_process(derivative, self.market)
        process_down = self.get_stochastic_process(derivative, self.market)
        process_up.S0 += epsilon  
        process_down.S0 -= epsilon
    
        price_up = self._get_price(derivative, process_up)
        price_down = self._get_price(derivative, process_down)
    
        delta = (price_up - price_down) / (2 * epsilon)
        return delta
    
    def get_gamma(self, derivative: AbstractOption, epsilon: float =0.1) -> float:
        """
        Calcule le gamma du produit, c'est-à-dire la seconde dérivée du prix par rapport 
        au prix du sous-jacent, en utilisant une différence finie centrée.

        Parameters:
            derivative (AbstractOption): Le produit à pricer.
            epsilon (float): La variation appliquée au prix du sous-jacent (par défaut 0.01).

        Returns:
            float: Le gamma calculé.
        """
        base_process = self.get_stochastic_process(derivative, self.market)
        base_price = self._get_price(derivative, base_process)
   
        process_up = self.get_stochastic_process(derivative, self.market)
        process_up.S0 += epsilon 
        process_down = self.get_stochastic_process(derivative, self.market)
        process_down.S0 -= epsilon
    
        price_up = self._get_price(derivative, process_up)
        price_down = self._get_price(derivative, process_down)
    
        gamma = (price_up + price_down - 2 * base_price) / (epsilon ** 2)
        return gamma

    def get_vega(self,derivative : AbstractOption,epsilon: float = 0.01) -> float:
        """
        Calcule le vega du produit, c'est-à-dire la dérivée du prix par rapport à la volatilité.

        Parameters:
            derivative (AbstractOption): Le produit à pricer.
            epsilon (float): La variation appliquée à la volatilité (par défaut 0.01).

        Returns:
            float: Le vega calculé.
        """
        vega = 0.0
        if(self.model.name == "BLACK_SCHOLES"):
 
            process_up = self.get_stochastic_process(derivative, self.market) 
            process_up.sigma += epsilon #temp voir comment bumper la surface de vol .. 
            process_down = self.get_stochastic_process(derivative, self.market)
            process_down.sigma -= epsilon
    
            price_up = self._get_price(derivative, process_up)
            price_down = self._get_price(derivative, process_down)
    
            vega = (price_up - price_down) / (2 * epsilon)
        return vega
    
    def get_vega2(self,derivative : AbstractOption,epsilon: float = 0.01) -> float:
        #on va bumper directement la market data et recalibrer la vol 

        vega = 0.0
        if(self.model.name == "BLACK_SCHOLES"):
            epsilon_fit = epsilon * 100 #les fichiers d'input sont en %
            bumped_market_up = self.market.bump_volatility(bump=epsilon_fit)
            bumped_market_down = self.market.bump_volatility(bump=-epsilon_fit)
            process_up = self.get_stochastic_process(derivative, bumped_market_up) 

            process_down = self.get_stochastic_process(derivative, bumped_market_down)
            
            vol_up = bumped_market_up.get_volatility(derivative.strike, derivative.maturity)
            vol = self.market.get_volatility(derivative.strike, derivative.maturity)
            vol_down = bumped_market_down.get_volatility(derivative.strike, derivative.maturity)

            #print("epsilon",epsilon)
            #print("diff up ",vol_up-vol)
            #print("diff down ",vol_down-vol)


            price_up = self._get_price(derivative, process_up)
            price_down = self._get_price(derivative, process_down)
    
            vega = (price_up - price_down) / (2 * epsilon)
        return vega
    
    def get_rho(self,derivative:AbstractOption,epsilon:float=0.0001):

        epsilon_fit = epsilon * 100 #les fichiers d'input sont en %
        market_up = self.market.bump_flat_yield_curve(epsilon_fit)
        market_down = self.market.bump_flat_yield_curve(-epsilon_fit)

        #test
        #print(market_up.get_rate(derivative.maturity) - self.market.get_rate(derivative.maturity))
        #print(epsilon)
        #print(market_down.get_rate(derivative.maturity) - self.market.get_rate(derivative.maturity))

        process_up = self.get_stochastic_process(derivative, market_up)
        process_down = self.get_stochastic_process(derivative, market_down)
        price_up = self._get_price(derivative, process_up)
        price_down = self._get_price(derivative, process_down)
        rho = (price_up - price_down) / (2 * epsilon)
        return rho
    

