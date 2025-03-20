from .abstract_interpolator import Interpolator
from scipy.interpolate import interp1d

class LinearInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        """
        Initializes the LinearInterpolator with market maturities and corresponding rates.

        Parameters:
            maturities (np.ndarray[float]): List of bond maturities.
            rates (np.ndarray[float]): List of observed yield rates corresponding to the maturities.
        """
        super().__init__(maturities, rates)
        self.interpolator = interp1d(maturities, rates, kind='linear', fill_value="extrapolate")

    def interpolate(self, t: float) -> float:
        """
        Interpolates the yield for a given maturity using the calibrated linear model.

        Parameters:
            t (float): Maturity at which to estimate the yield.

        Returns:
            float: Estimated yield rate for the given maturity.
        """
        return self.interpolator(t)