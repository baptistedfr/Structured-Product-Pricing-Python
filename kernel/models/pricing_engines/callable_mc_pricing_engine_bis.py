from .mc_pricing_engine_bis import MCPricingEngineBis
from kernel.tools import ObservationFrequency
from kernel.products.structured_products import AbstractAutocall
from kernel.market_data import Market
from kernel.models.stochastic_processes import StochasticProcess
from utils.pricing_settings import PricingSettings
from utils.pricing_results import PricingResults
from kernel.models.discritization_schemes.euler_scheme import EulerSchemeBis

import numpy as np


class CallableMCPricingEngineBis(MCPricingEngineBis):
    """
    A Monte Carlo pricing engine for callable financial derivatives.

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """

    def __init__(self, market: Market, settings: PricingSettings) -> None: # type: ignore
        super().__init__(market, settings)
        self.obs_frequency = settings.obs_frequency
        self.compute_coupon = settings.compute_callable_coupons

    def get_results(self, derivative) -> PricingResults: 
        result = PricingResults()
        self._set_stochastic_process(derivative)

        if (self.compute_coupon):
            coupon = self.get_coupon(derivative) #voir pour la paramétrisation du target price
            result.coupon_callable = coupon
        else :
            price = self.get_price(derivative, self.stochastic_process)
            result.price = price
        return result

    def get_price(self, derivative: AbstractAutocall, process : StochasticProcess) -> float:

        scheme = EulerSchemeBis()
        paths = scheme.simulate_paths(process, self.nb_paths, self.random_seed)
        total_payoff = []
        for path in paths:
            # For each path we compute the cashflow sum according to the callable parameters and the index of the call date
            payoff, t_call = derivative.payoff(path)
            # Mapping from the index of the call date to the number of year
            discount_time = t_call * self.obs_frequency.value
            # We discount the sum of cashflow frow the call date to the present date
            total_payoff.append(payoff * self.market.get_discount_factor(discount_time))
        return np.mean(total_payoff)

    def get_coupon(self, derivative: 'CallableProduct', epsilon: float = 1e-2, max_iter: int = 25, target_price: float = 100) -> float: # type: ignore
        """
        Computes the coupon of the structured product such that the price equals the target price (e.g., initial capital).

        Parameters:
            derivative (CallableProduct): The derivative for which to compute the coupon.
            epsilon (float): The tolerance for the price difference, default is 1e-6.
            max_iter (int): The maximum number of iterations for the dichotomy method, default is 100.
            target_price (float): The target price, default is 100

        Returns:
            float: The computed coupon.
        """
        # Define the bounds for the coupon (%)
        lower_bound = 0.0
        upper_bound = 50.0

        for _ in range(max_iter):
            mid_coupon = (lower_bound + upper_bound) / 2.0

            # Set the coupon in the derivative
            derivative.coupon_rate = mid_coupon

            # Compute the price for the current coupon
            price = self.get_price(derivative,self.stochastic_process)

            # Check if the price is close enough to the target price
            if abs(price - target_price) < epsilon:
                return mid_coupon
            
            if price < target_price:
                lower_bound = mid_coupon
            else:
                upper_bound = mid_coupon

        return mid_coupon