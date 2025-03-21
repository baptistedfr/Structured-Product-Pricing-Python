import numpy as np
from scipy.stats import norm
from .abstract_sheme import AbstractScheme

class EulerScheme(AbstractScheme):
    """
    Class implementing the Euler scheme for simulating stochastic paths.
    Inherits from AbstractScheme.
    """

    def __init__(self, process, seed=4012, nb_paths=10000):
        """
        Initialize the Euler scheme.

        Parameters:
            process (StochasticProcess): The stochastic process to simulate.
            seed (int): Seed for the random number generator. Default is 4012.
            nb_paths (int): Number of paths to simulate. Default is 10000.
        """
        super().__init__(process, seed, nb_paths)

    def simulate_paths(self):
        """
        Simulate stochastic paths using the Euler scheme.

        Returns:
            np.ndarray: A NumPy array containing the simulated paths.
        """
        # Generate the random processes
        brownian_increments = self._generate_random_increments()
        
        # Initialize the paths with initial values
        paths = np.zeros((self.nb_paths, self.process.nb_steps + 1))
        paths[:, 0] = self.process.initial_value
        
        # Compute the stochastic processes
        factors = self.process.drift * self.process.dt + self.process.diffusion * brownian_increments
        
        # Apply the Euler scheme
        paths[:, 1:] = self.process.initial_value * np.cumprod(1 + factors, axis=1)

        return paths
