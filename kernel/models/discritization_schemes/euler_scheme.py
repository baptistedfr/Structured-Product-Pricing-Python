import numpy as np
from typing import Tuple
from .abstract_sheme import AbstractScheme
from ..stochastic_processes.black_scholes_process import BlackScholesProcess

class EulerScheme(AbstractScheme):
    """
    Class implementing the Euler scheme for simulating stochastic paths of the underlying asset.
    """

    def __init__(self, process: BlackScholesProcess, nb_paths: float = 10000, seed: int = 4012):
        """
        Initializes an instance of the AbstractScheme class.

        Parameters:
            stochastic_process (BlackScholesProcess): The BS stochastic process to simulate
            nb_paths (float): The number of paths to simulate. Default is 10000
            seed (int): The seed for the random number generator. Default is 4012
        """
        self.process = process
        self.nb_paths = nb_paths
        self.seed = seed

    def simulate_paths(self) -> Tuple[np.ndarray, None]:
        """
        Simulate stochastic paths using the path Euler Scheme.

        Returns:
            Tuple[np.ndarray, None]: A NumPy array containing the simulated paths.
        """
        # Generate the random brownian increments
        W = self._generate_random_increments()

        mu = self.process.drift
        sigma = self.process.diffusion

        # Initialize the matrix of paths and set the initial value
        S = np.zeros((self.nb_paths, self.process.nb_steps + 1))
        S[:, 0] = self.process.S0

        # Compute the paths using the Euler scheme
        for i in range(1, self.process.nb_steps + 1):
            S[:, i] = S[:, i - 1] * np.exp((mu[i-1] - 0.5 * sigma**2) * self.process.dt + sigma * W[:, i - 1])

        return S, None
