import numpy as np
from .abstract_interpolator import Interpolator
from scipy.interpolate import CubicSpline

class CubicInterpolator(Interpolator):

    def __init__(self, maturities: np.ndarray[float], rates: np.ndarray[float]):
        """
        Initializes the CubicInterpolator with market maturities and corresponding rates.

        Parameters:
            maturities (np.ndarray[float]): List of bond maturities.
            rates (np.ndarray[float]): List of observed yield rates corresponding to the maturities.
        """
        super().__init__(maturities, rates)

        self.interpolator = CubicSpline(maturities, rates, bc_type='natural', extrapolate=True)

    def interpolate(self, t: float) -> float:
        """
        Interpolates the yield for a given maturity using the calibrated CubicSpline model.

        Parameters:
            t (float): Maturity at which to estimate the yield.

        Returns:
            float: Estimated yield rate for the given maturity.
        """
        return self.interpolator(t)