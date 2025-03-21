from ..stochastic_processes.stochastic_process import StochasticProcess
from abc import ABC, abstractmethod
import numpy as np


class AbstractScheme(ABC):
    """
    Abstract class representing a discretization scheme to simulate paths of a stochastic process.

    Attributes:
        stochastic_process (StochasticProcess): The stochastic process to simulate
        seed (int): The seed for the random number generator
        nb_paths (float): The number of paths to simulate
    """

    def __init__(self, process: StochasticProcess, seed: int = 4012, nb_paths: float = 10000):
        """
        Initializes an instance of the AbstractScheme class.

        Parameters:
            stochastic_process (StochasticProcess): The stochastic process to simulate
            seed (int): The seed for the random number generator. Default is 4012
            nb_paths (float): The number of paths to simulate. Default is 10000
        """
        self.process = process
        self.seed = seed
        self.nb_paths = nb_paths

        self._generate_random_increments()
        
    def _generate_random_increments(self):
        """
        Generates random increments of the brownian motion.

        Returns:
            np.ndarray: The generated increments for the stochastic process
        """
        return self.process.get_brownian_increments(self.seed, self.nb_paths)

    @abstractmethod
    def simulate_paths(self):
        """
        Simulates paths of the stochastic process.

        Returns:
            np.ndarray: The simulated paths of the stochastic process
        """
        ...