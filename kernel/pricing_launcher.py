from kernel.market_data import Market
from kernel.models.stochastic_processes import *
from kernel.models.pricing_engines import PricingEngineType
from kernel.products.abstract_derive import AbstractDerive
from typing import Union


class PricingLauncher:
    """
    The pricing launcher defines the objects used for the pricing as follow:
        - Based on the selected diffusion (BS, Heston...) the associated stochastic process is defined
    """

    def __init__(self, market: Market, nb_paths: float, nb_steps: float, 
                 pricer_type: PricingEngineType, discretization_method: 'EulerSchemeType'): # type: ignore
        """
        Initializes the pricing engine.

        Parameters:
            market (Market): The market data used for pricing
            nb_paths (float): The number of paths to simulate
            nb_steps (float): The number of steps to simulate for each path
            discretization_type (EulerSchemeType): The type of discretization scheme to use. Default is EulerSchemeType.EULER
        """
        self.market = market
        self.pricer_type = pricer_type
        self.discretization_method = discretization_method
        self.nb_paths = nb_paths
        self.nb_steps = nb_steps

    def _define_process(self, derivative: AbstractDerive) -> Union[BlackScholesProcess, HestonProcess]:
        """
        Defines the stochastic process used for simulation based on market & derivatives parameters.

        Parameters:
            derivatives (AbstractDerive): derivative to price

        Returns:
            BlackScholesProcess | HestonProcess : The stochastic process used for simulation.
        """
        # Derivates parameters
        T = derivative.maturity
        K = derivative.strike

        # Market parameters
        initial_value = self.market.underlying_asset.last_price
        drift = self.market.get_rate(T)
        volatility = self.market.get_volatility(K, T)
        
        if self.discretization_method.name == "EULER":
            return BlackScholesProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, volatility=volatility)
        
        elif self.discretization_method.name == "HESTON_EULER":
            theta = volatility**2
            kappa = 1
            ksi = 0.1
            rho = -0.5
            return HestonProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, theta=theta, kappa=kappa, ksi=ksi, rho=rho)
        
        else:
            raise ValueError("Wrong discretization process selected !")
        
    def price(self, derivative: AbstractDerive) -> float:
        """
        Calls the right pricing engine with the defined process to price the derivatives.

        Parameters:
            derivatives (AbstractDerive): derivative to price

        Returns:
            float: price of the derivatives
        """
        process = self._define_process(derivative)

        self.pricer = self.pricer_type.value(market=self.market, nb_paths=self.nb_paths, nb_steps=self.nb_steps,
                                        discretization_method=self.discretization_method, stochastic_process=process)
        
        return self.pricer.compute_price(derivative)