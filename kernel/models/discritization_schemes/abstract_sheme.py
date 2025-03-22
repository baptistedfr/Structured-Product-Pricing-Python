from abc import ABC, abstractmethod
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Union

class AbstractScheme(ABC):
    """
    Abstract class representing a discretization scheme to simulate paths of a stochastic process.

    Attributes:
        stochastic_process (StochasticProcess): The stochastic process to simulate
        seed (int): The seed for the random number generator
        nb_paths (float): The number of paths to simulate
    """

    def __init__(self, process: 'StochasticProcess', nb_paths: float = 10000, seed: int = 4012): # type: ignore
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
        
    @abstractmethod
    def simulate_paths(self) -> np.ndarray:
        """
        Simulates paths of the stochastic process.

        Returns:
            np.ndarray: The simulated paths of the stochastic process
        """
        ...

    def _generate_random_increments(self) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Generates random increments underlying asset brownian motion.

        Returns:
            np.ndarray: The generated increments for the brownian motion
                or
            tuple(np.ndarray): The generated increments for the brownian motions if the process has multiple sources of randomness
        """
        return self.process.get_random_increments(nb_paths=self.nb_paths, seed=self.seed)


    def plot_paths(self, nb_paths_plot: int, plot_variance: bool = False):
        """
        Plot the first simulated paths of the underlying asset.
        """
        S_paths, _ = self.simulate_paths()
        S_paths = S_paths[:nb_paths_plot, :]

        sns.set(style="whitegrid")
        palette = sns.color_palette("RdYlBu", nb_paths_plot)
        for i in range(S_paths.shape[0]):
            plt.plot(S_paths[i, :], color=palette[i])
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlim(0, self.process.nb_steps)
        plt.xlabel('Time step', fontsize=12)
        plt.ylabel('Underlying Price', fontsize=12)
        plt.title('Price paths simulated by the Euler scheme', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
