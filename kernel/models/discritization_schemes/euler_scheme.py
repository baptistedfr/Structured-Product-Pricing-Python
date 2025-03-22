import numpy as np
from .abstract_sheme import AbstractScheme
import matplotlib.pyplot as plt
import seaborn as sns


class EulerScheme(AbstractScheme):
    """
    Class implementing the Euler scheme for simulating stochastic paths.
    """

    def simulate_paths(self):
        """
        Simulate stochastic paths using the path Euler Scheme.

        Returns:
            np.ndarray: A NumPy array containing the simulated paths.
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
            S[:, i] = S[:, i - 1] * np.exp((mu - 0.5 * sigma**2) * self.process.dt + sigma * W[:, i - 1])

        return S
    
    def plot_paths(self, nb_paths_plot: int):
        """
        Plot the first simulated paths with improved aesthetics.
        """
        sns.set(style="whitegrid")
        palette = sns.color_palette("RdYlBu", nb_paths_plot)
        paths = self.simulate_paths()[:nb_paths_plot, :]
        for i in range(paths.shape[0]):
            plt.plot(paths[i, :], color=palette[i])
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlim(0, self.process.nb_steps)
        plt.xlabel('Time step', fontsize=12)
        plt.ylabel('Underlying Price', fontsize=12)
        plt.title('Price paths simulated by the Euler scheme', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
