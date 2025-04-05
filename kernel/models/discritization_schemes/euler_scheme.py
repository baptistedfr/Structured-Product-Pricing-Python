import numpy as np
from typing import Tuple
from .abstract_sheme import AbstractScheme
from ..stochastic_processes.black_scholes_process import BlackScholesProcess
from ..stochastic_processes.stochastic_process import StochasticProcess,OneFactorStochasticProcess,TwoFactorStochasticProcess

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
    

class EulerSchemeBis:
    
    def simulate_paths(self, process: StochasticProcess, nb_paths: int, seed: int = 4012) -> np.ndarray:
        if isinstance(process, OneFactorStochasticProcess):
            return self._simulate_one_factor(process, nb_paths, seed)
        elif isinstance(process, TwoFactorStochasticProcess):
            return self._simulate_two_factor(process, nb_paths, seed)
        else:
            raise NotImplementedError("Only OneFactor or TwoFactor processes are supported.")

    def _simulate_one_factor(self, process: OneFactorStochasticProcess, nb_paths: int, seed: int) -> np.ndarray:
        paths = np.zeros((nb_paths, process.nb_steps + 1))
        S = np.zeros((nb_paths, process.nb_steps + 1))

        paths[:, 0] = process.S0
        S[:, 0] = process.S0
        dt = process.dt
        dW = process.get_random_increments(nb_paths, seed)

        for i in range(process.nb_steps):
            t = i * dt
            x = paths[:, i]
            dW_i = dW[:, i]
            drift = process.get_drift(i, x)
            vol = process.get_volatility(i, x)
            mu = drift / x

            paths[:, i + 1] = x + drift * dt + vol  * dW_i
            S[:, i+1] = S[:, i - 1] * np.exp((mu - 0.5 * vol**2) * dt + vol * dW[:, i ])
        return paths

    def _simulate_two_factor(self, process: TwoFactorStochasticProcess, nb_paths: int, seed: int) -> np.ndarray:
        paths = np.zeros((nb_paths, process.nb_steps + 1, 2))
        paths[:, 0, 0] = process.S0
        paths[:, 0, 1] = process.V0
        dt = process.dt
        sqrt_dt = np.sqrt(dt)

        for i in range(process.nb_steps):
            t = i * dt
            x = paths[:, i, 0]
            v = paths[:, i, 1]
            dW1, dW2 = process.get_random_increments(nb_paths, seed + i)

            drift = process.get_drift(i, x)
            vol_drift = process.get_vol_drift(i, v)
            vol_vol = process.get_vol_vol(i, v)

            x_next = x + drift * dt + np.sqrt(np.maximum(v, 0)) * x * sqrt_dt * dW1
            v_next = v + vol_drift * dt + vol_vol * sqrt_dt * dW2

            paths[:, i + 1, 0] = x_next
            paths[:, i + 1, 1] = v_next

        return paths
