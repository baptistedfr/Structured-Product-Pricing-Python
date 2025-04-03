from .mc_pricing_engine import MCPricingEngine
from kernel.tools import ObservationFrequency
import numpy as np


class CallableMCPricingEngine(MCPricingEngine):
    """
    A Monte Carlo pricing engine for callable financial derivatives.

    This class uses Monte Carlo simulation to compute the price of derivatives
    and can be extended to compute Greeks or other risk measures.
    """

    def compute_price(self, derivative: 'CallableProduct', obs_frequency: ObservationFrequency = ObservationFrequency.ANNUAL) -> float: #type: ignore # A changer avec la bonne classe le moment venu
        """
        Computes the price of a structured product using the Monte Carlo simulation.

        Parameters:
            derivative (AbstractOption): The derivative to price.
            obs_frequency (ObservationFrequency): The observation frequency of the structured contract, default is annual

        Returns:
            float: The computed price of the derivative.
        """
        # Define the stochastic process
        self.process = self.stochastic_process(derivative)

        # Define the scheme used for the discretization
        self.scheme = self.discretization_method.value(self.process, nb_paths=self.nb_paths)
        
        # Simulate paths and compute the payoff
        price_paths, _ = self.scheme.simulate_paths()

        total_payoff = []
        for path in price_paths:
            # For each path we compute the cashflow sum according to the callable parameters and the index of the call date
            payoff, t_call = derivative.payoff(path)
            # Mapping from the index of the call date to the number of year
            discount_time = t_call * obs_frequency.value
            # We discount the sum of cashflow frow the call date to the present date
            total_payoff.append(payoff * np.exp(-self.process.drift * discount_time))
        
        # NPV sum
        return np.mean(total_payoff)

    def compute_coupon(self, derivative: 'CallableProduct', epsilon: float = 1e-6, max_iter: int = 100) -> float: # type: ignore
        """
        Computes the coupon of the structured product such that the price equals the target price (e.g., initial capital).

        Parameters:
            derivative (CallableProduct): The derivative for which to compute the coupon.
            target_price (float): The target price (e.g., initial capital).
            epsilon (float): The tolerance for the price difference, default is 1e-6.
            max_iter (int): The maximum number of iterations for the dichotomy method, default is 100.

        Returns:
            float: The computed coupon.
        """
        # Target price = initial capital
        target_price = derivative.capital # A modifier en fonction de l'attribut de la classe produit callable

        # Define the bounds for the coupon (%)
        lower_bound = 0.0
        upper_bound = 0.5

        for _ in range(max_iter):
            mid_coupon = (lower_bound + upper_bound) / 2.0

            # Set the coupon in the derivative
            derivative.coupon = mid_coupon

            # Compute the price for the current coupon
            price = self.compute_price(derivative)

            # Check if the price is close enough to the target price
            if abs(price - target_price) < epsilon:
                return mid_coupon
            
            if price < target_price:
                lower_bound = mid_coupon
            else:
                upper_bound = mid_coupon

        return mid_coupon