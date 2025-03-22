import numpy as np
from scipy.stats import norm
from .abstract_sheme import AbstractScheme
from ..stochastic_processes.stochastic_process import StochasticProcess


class PathIndependentScheme(AbstractScheme):
    """
    Class implementing the scheme for simulating stochastic paths.
    Inherits from AbstractScheme.
    """

    def __init__(self, process: StochasticProcess, nb_paths: float = 10000, seed: int = 4012):
        """
        Parameters:
            stochastic_process (StochasticProcess): The stochastic process to simulate
            nb_paths (float): The number of paths to simulate. Default is 10000
            seed (int): The seed for the random number generator. Default is 4012     
        """
        self.process = process
        self.seed = seed
        self.nb_paths = nb_paths

    def simulate_paths(self) -> np.ndarray:
        """
        Simulate stochastic paths using the path independent scheme, only computing the last point.

        Returns:
            np.ndarray: A NumPy array containing the simulated terminal values.
        """
        W = self._generate_random_increments()

        mu = self.process.drift
        sigma = self.process.diffusion

        return self.process.S0 * np.exp((mu - 0.5 * sigma**2) * self.process.T + sigma * W)
