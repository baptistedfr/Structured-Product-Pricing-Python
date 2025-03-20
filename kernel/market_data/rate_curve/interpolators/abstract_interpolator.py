import numpy as np
from abc import ABC, abstractmethod

class Interpolator(ABC):

    def __init__(self, maturities: np.ndarray[float], rates: np.ndarray[float]):
        """
        Initializes the interpolator with observed market rates and calibrates it.

        Parameters:
            maturities (np.ndarray[float]): Array of maturities (in years).
            rates (np.ndarray[float]): Array of observed yield rates corresponding to the maturities.
        """
        self.maturities = maturities
        self.rates = rates

    @abstractmethod
    def interpolate(self, t: float) -> float:
        """
        Interpolates the yield for a given maturity.

        Parameters:
            t (float): Maturity at which to estimate the yield.

        Returns:
            float: Estimated yield rate for the given maturity.
        """
        pass
