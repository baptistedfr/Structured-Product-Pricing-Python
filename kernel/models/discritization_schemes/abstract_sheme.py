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

    def __init__(self, process: StochasticProcess, nb_paths: float = 10000, seed: int = 4012):
        """
        Initializes an instance of the AbstractScheme class.

        Parameters:
            stochastic_process (StochasticProcess): The stochastic process to simulate
            nb_paths (float): The number of paths to simulate. Default is 10000
            seed (int): The seed for the random number generator. Default is 4012
        """
        self.process = process
        self.seed = seed
        self.nb_paths = nb_paths
        
    def _generate_random_increments(self) -> np.ndarray:
        """
        Generates random increments of the brownian motion.

        Returns:
            np.ndarray: The generated increments for the stochastic process
        """
        return self.process.get_brownian_increments(nb_paths=self.nb_paths, seed=self.seed)

    @abstractmethod
    def simulate_paths(self) -> np.ndarray:
        """
        Simulates paths of the stochastic process.

        Returns:
            np.ndarray: The simulated paths of the stochastic process
        """
        ...