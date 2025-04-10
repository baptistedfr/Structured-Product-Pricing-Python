from .abstract_pricing_engine import AbstractPricingEngine
from ..stochastic_processes import StochasticProcess
from kernel.products.options.abstract_option import AbstractOption
from kernel.market_data.market import Market
from kernel.products.options.americain_options import *
from kernel.tools import ObservationFrequency
from utils.pricing_settings import PricingSettings
from utils.pricing_results import PricingResults
from kernel.models.stochastic_processes import BlackScholesProcess,HestonProcess
from kernel.models.stochastic_processes.black_scholes_process import BlackScholesProcess
from kernel.models.discritization_schemes.euler_scheme import EulerScheme
from .mc_pricing_engine import MCPricingEngine
import numpy as np
import pandas as pd


class AmericanMCPricingEngine(MCPricingEngine):
    """
    A Monte Carlo pricing engine for classic financial derivatives (no barrier, no asian payoff ...)

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """
    def __init__(self, market: Market, settings: PricingSettings) -> None: # type: ignore
        super().__init__(market, settings)

    def get_results(self, derivative : AmericanAbstractOption) -> PricingResults: 
        result = PricingResults()
        self._set_stochastic_process(derivative)
        price = self._get_price(derivative, self.stochastic_process)
        result.price = price

        return result

    def _get_price(self, derivative : AmericanAbstractOption , stochastic_process : StochasticProcess) -> float:
        
        scheme = EulerScheme()
        paths=scheme.simulate_paths(process=stochastic_process, nb_paths=self.nb_paths, seed=self.random_seed)


        dt = derivative.maturity / self.nb_steps

        exercise_indices = None
        if derivative.exercise_times is not None:
            exercise_indices = set(int(t_ex / dt) for t_ex in derivative.exercise_times)

        CF = derivative.instrinsec_payoff(paths[:, -1])
        for t in range(self.nb_steps - 2, -1, -1):
            df_forward = self.market.get_fwd_discount_factor(dt * (t + 1),dt * (t + 2))
            discounted_CF = CF * df_forward
            CF = discounted_CF.copy()
            
            if exercise_indices is None or t in exercise_indices: 
                immediate = derivative.instrinsec_payoff(paths[:, t])
                in_money = (immediate > 0)

                if np.any(in_money):
                    X = np.column_stack([
                        np.ones(np.sum(in_money)),
                        paths[in_money, t],
                        paths[in_money, t] ** 2
                    ])
                    Y = discounted_CF[in_money]
                    coeff, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
                    cont_val = coeff[0] + coeff[1] * paths[in_money, t] + coeff[2] * (paths[in_money, t] ** 2)
                    exercise = immediate[in_money] >= cont_val
                    CF[in_money] = np.where(exercise, immediate[in_money], discounted_CF[in_money])

                
        return self.market.get_discount_factor(dt) * np.mean(CF)
