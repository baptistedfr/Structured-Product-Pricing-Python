from .abstract_interpolator import Interpolator
import numpy as np
from scipy.optimize import curve_fit

class NelsonSiegelInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        self.maturities = np.array(maturities)
        self.rates = np.array(rates)

        self.beta0, self.beta1, self.beta2, self.tau = self._calibrate

    @staticmethod
    def _nelson_siegel(t, beta0, beta1, beta2, tau):
        return beta0 + beta1 * (1 - np.exp(-t / tau)) / (t / tau) + beta2 * (
                    (1 - np.exp(-t / tau)) / (t / tau) - np.exp(-t / tau))

    def _calibrate(self):
        p0 = [0.02, -0.02, 0.02, 1.0]
        params, _ = curve_fit(self._nelson_siegel, self.maturities, self.rates, p0=p0,
                              bounds=([0, -np.inf, -np.inf, 0.01], [np.inf, np.inf, np.inf, np.inf]))
        return params