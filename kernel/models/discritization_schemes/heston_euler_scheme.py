import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Tuple, Union
from .abstract_sheme import AbstractScheme
from ..stochastic_processes.heston_process import HestonProcess


class HestonEulerScheme(AbstractScheme):
    """
    Class implementing the Euler scheme for simulating stochastic paths of the Heston process.
    We choose to implement the 'Full truncation method' for the discretization of the volatility process to ensure the positivity of the variance.
    """
    
    def __init__(self, process: HestonProcess, nb_paths: int = 10000, seed:int = 4012):
        """
        Initializes an instance of the HestonEulerScheme class.

        Parameters:
            process (HestonProcess): The Heston process to simulate
            nb_paths (int): The number of paths to simulate. Default is 10000
            seed (int): The seed for the random number generator. Default is 4012
        """
        self.process = process
        self.nb_paths = nb_paths
        self.seed = seed

    def simulate_paths(self, return_variance: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate stochastic paths using the path Heston process, i.e. the underlying asset and the volatility processes.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple of NumPy arrays containing the simulated paths of the underlying asset and the volatility processes
        """
        # Generate the random brownian increments for both the underlying asset and the volatility processes
        W1, W2 = self._generate_random_increments()

        # Initialize the matrix of paths and set the initial value for both the underlying asset and the volatility processes
        S = np.zeros((self.nb_paths, self.process.nb_steps + 1))
        V = np.zeros((self.nb_paths, self.process.nb_steps + 1))
        S[:, 0] = self.process.S0
        V[:, 0] = self.process.theta

        # Compute the paths using the Heston Euler scheme
        for i in range(1, self.process.nb_steps + 1):
            S[:, i] = S[:, i - 1] * np.exp((self.process.drift - 0.5 * np.max(V[:, i - 1], 0)) * self.process.dt + np.sqrt(np.max(V[:, i - 1], 0)) * W1[:, i - 1])
            V[:, i] = V[:, i - 1] + self.process.kappa * (self.process.theta - np.max(V[:, i - 1], 0)) * self.process.dt + \
                      self.process.ksi * np.sqrt(np.max(V[:, i - 1], 0)) * W2[:, i - 1]

        if return_variance:
            return S, V 
        else:
            return S, None

    def plot_paths(self, nb_paths_plot: int, plot_variance: bool = False):
        """
        Plot the first simulated paths of both the underlying asset and the volatility processes.
        """
        S_paths, V_paths = self.simulate_paths(return_variance=plot_variance)
        S_paths = S_paths[:nb_paths_plot, :]
        if plot_variance and V_paths is not None:
            V_paths = V_paths[:nb_paths_plot, :]

        sns.set(style="whitegrid")
        palette = sns.color_palette("RdYlBu", nb_paths_plot)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        for i in range(S_paths.shape[0]):
            axes[0].plot(S_paths[i, :], color=palette[i])
        axes[0].grid(True, linestyle='--', alpha=0.7)
        axes[0].set_xlim(0, self.process.nb_steps)
        axes[0].set_xlabel('Time step', fontsize=12)
        axes[0].set_ylabel('Underlying Price', fontsize=12)
        axes[0].set_title('Unlying price paths simulated by the Heston Euler scheme', fontsize=14, fontweight='bold')
        
        if plot_variance:
            for i in range(V_paths.shape[0]):
                axes[1].plot(V_paths[i, :], color=palette[i])
            axes[1].grid(True, linestyle='--', alpha=0.7)
            axes[1].set_xlim(0, self.process.nb_steps)
            axes[1].set_xlabel('Time step', fontsize=12)
            axes[1].set_ylabel('Variance', fontsize=12)
            axes[1].set_title('Variance paths simulated by the Heston Euler scheme', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.show()