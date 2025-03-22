from .mc_pricing_engine import MCPricingEngine
from ..stochastic_processes.heston_process import HestonProcess
from kernel.products.options.abstract_option import AbstractOption


class HestonMCPricingEngine(MCPricingEngine):
    """
    A Monte Carlo pricing engine for path independent financial derivatives with Heson stochastic volatility model.
    """

    def _define_process(self, derivative: AbstractOption) -> HestonProcess:
        """
        Defines the Heston stochastic process with correct parametrization.

        Returns:
            HestonProcess: The stochastic process used for simulation.
        """
        # Derivates parameters
        T = derivative.maturity
        K = derivative.strike

        # Market parameters
        initial_value = self.market.underlying_asset.last_price
        drift = self.market.get_rate(T) / 100
        volatility = self.market.get_volatility(K, T*252) # Corriger la maturité de jours en années dans les fichiers de vol
        theta = volatility**2
        kappa = 1
        ksi = 0.1
        rho = -0.5
        
        return HestonProcess(S0=initial_value, T=T, nb_steps=self.nb_steps, drift=drift, theta=theta, kappa=kappa, ksi=ksi, rho=rho)
