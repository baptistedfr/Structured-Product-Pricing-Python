from kernel.models.stochastic_processes.stochastic_process import StochasticProcess,TwoFactorStochasticProcess
import numpy as np
from typing import Tuple

class HestonProcess(StochasticProcess):
    """
    Class representing a Heston process.
    Inherits from StochasticProcess.
    """

    def __init__(self, S0: float, T: float, nb_steps: int, drift: float, theta: float, kappa: float, ksi: float, rho: float):
        """
        Initializes the stochastic process.

        Parameters:
            S0 (float): The initial value of the process
            T (float): The maturity of the process
            nb_steps (int): The number of steps to simulate
            drift (float): The drift of the underlying asset process
            theta (float): The long-term average variance
            kappa (float): The mean reversion speed
            ksi (float): The volatility of the volatility
            rho (float): The correlation between the underlying brownian motion and the volatility brownian motion
        """
        super().__init__(S0, T, nb_steps)
        self.drift = drift
        self.theta = theta
        self.kappa = kappa
        self.ksi = ksi
        self.rho = rho
        self.nb_factors = 2  # Number of factors in the Heston model (underlying and volatility) 

    def get_random_increments(self, nb_paths: int, seed: int = 4012) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates the two correlated brownian motions of the Heston process with the Cholesky decomposition.

        Parameters:
            nb_paths (int): The number of paths to simulate
            seed (int): The seed for the random number generator. Default is 4012
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: The generated increments for the two correlated brownian motions
        """
        # We use two seeds to generate two independent random number generators
        rng = np.random.default_rng(seed)
        rng2 = np.random.default_rng(seed + 1)

        # Generate the two independent brownian motions
        Z1 = rng.standard_normal(size=(nb_paths, self.nb_steps))
        Z2 = rng2.standard_normal(size=(nb_paths, self.nb_steps))   

        # Apply the Cholesky decomposition to get the correlated brownian motions 
        Z3 = self.rho * Z1 + np.sqrt(1 - self.rho**2) * Z2

        return Z1 * np.sqrt(self.dt), Z3 * np.sqrt(self.dt)
    

class HestonProcessBis(TwoFactorStochasticProcess): #pas encore bien implementé, à revoir 
    def __init__(self, S0, V0, r, kappa, theta, xi, rho, T, nb_steps):
        super().__init__(S0, T, nb_steps, nb_factors=2)
        self.V0 = V0
        self.r = r
        self.kappa = kappa
        self.theta = theta
        self.xi = xi
        self.rho = rho

    def get_drift(self, t, x):
        return self.r * x
    def get_vol_drift(self, t, v):
        return self.kappa * (self.theta - v)
    def get_vol_vol(self, t, v):
        return self.xi * np.sqrt(np.maximum(v, 0))
    def get_random_increments(self, nb_paths: int, seed: int = 4012) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates the two correlated brownian motions of the Heston process with the Cholesky decomposition.

        Parameters:
            nb_paths (int): The number of paths to simulate
            seed (int): The seed for the random number generator. Default is 4012
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: The generated increments for the two correlated brownian motions
        """
        # We use two seeds to generate two independent random number generators
        rng = np.random.default_rng(seed)
        rng2 = np.random.default_rng(seed + 1)

        # Generate the two independent brownian motions
        Z1 = rng.standard_normal(size=(nb_paths, self.nb_steps))
        Z2 = rng2.standard_normal(size=(nb_paths, self.nb_steps))   

        # Apply the Cholesky decomposition to get the correlated brownian motions 
        Z3 = self.rho * Z1 + np.sqrt(1 - self.rho**2) * Z2

        return Z1 * np.sqrt(self.dt), Z3 * np.sqrt(self.dt)
        