from kernel.models.stochastic_processes.stochastic_process import StochasticProcess,OneFactorStochasticProcess
import numpy as np


class BlackScholesProcess(StochasticProcess):
    """
    Class representing a Black-Scholes process.
    Inherits from StochasticProcess.
    """

    def __init__(self, S0: float, T: float, nb_steps: int, drift:np.ndarray, volatility: float):
        """
        Initializes the stochastic process.

        Parameters:
            S0 (float): The initial value of the process
            T (float): The maturity of the process
            nb_steps (int): The number of steps to simulate
            drift (float): The drift of the process
            volatility (float): The volatility of the process
        """
        super().__init__(S0, T, nb_steps)
        self.drift = drift
        self.diffusion = volatility 

    def get_random_increments(self, nb_paths, seed = 4012):
        """
        Generates random increments of the brownian motion of Black-Scholes process.

        Parameters:
            nb_paths (int): The number of paths to simulate
            seed (int): The seed for the random number generator. Default is 4012
        
        Returns:
            np.ndarray: The generated increments for the brownian motion
        """
        rng = np.random.default_rng(seed)
        Z = rng.standard_normal(size=(nb_paths, self.nb_steps))
        return Z * np.sqrt(self.dt)
    
class BlackScholesProcessBis(OneFactorStochasticProcess):
    """
    Class representing a Black-Scholes process.
    Inherits from StochasticProcess.
    """

    def __init__(self, S0: float, T: float, nb_steps: int, drift:np.ndarray, volatility: float):
        """
        Initializes the stochastic process.

        Parameters:
            S0 (float): The initial value of the process
            T (float): The maturity of the process
            nb_steps (int): The number of steps to simulate
            drift (float): The drift of the process
            volatility (float): The volatility of the process
        """
        super().__init__(S0, T, nb_steps)
        self.mu = drift
        self.sigma = volatility 
    
    def get_drift(self, t, x):
        return self.mu[t] * x

    def get_volatility(self, t, x):
        return self.sigma * x
    
    def get_random_increments(self, nb_paths, seed = 4012):
        """
        Generates random increments of the brownian motion of Black-Scholes process.

        Parameters:
            nb_paths (int): The number of paths to simulate
            seed (int): The seed for the random number generator. Default is 4012
        
        Returns:
            np.ndarray: The generated increments for the brownian motion
        """
        rng = np.random.default_rng(seed)
        Z = rng.standard_normal(size=(nb_paths, self.nb_steps))
        return Z * np.sqrt(self.dt)