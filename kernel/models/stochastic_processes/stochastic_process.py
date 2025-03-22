from abc import ABC, abstractmethod
import numpy as np
from typing import Union, Tuple

class StochasticProcess(ABC):
    """
    Abstract class representing a stochastic process.
    """

    def __init__(self, S0: float, T: float, nb_steps: int):
        """
        Initializes the stochastic process.

        Parameters:
            S0 (float): The initial value of the process
            T (float): The maturity of the process
            nb_steps (int): The number of steps to simulate
        """
        dt = T / nb_steps
        if dt <= 0:
            raise ValueError("Le temps (dt) doit être positif.")
        if nb_steps <= 0:
            raise ValueError("Le nombre de pas doit être positif.")
        
        self.S0 = S0
        self.nb_steps = nb_steps
        self.T = T
        self.dt = dt

    @abstractmethod
    def get_random_increments(self, nb_paths: int, seed: int = 4012) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Generates random increments of the brownian motion(s).

        Parameters:
            nb_paths (int): The number of paths to simulate
            seed (int): The seed for the random number generator. Default is 4012
        
        Returns:
            np.ndarray: The generated increments for the brownian motion
                or
            tuple(np.ndarray): The generated increments for the brownian motions if the process has multiple sources of randomness
        """
        pass
