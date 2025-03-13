from .abstract_interpolator import Interpolator
from scipy.optimize import curve_fit
import numpy as np


class SvenssonInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        self.maturities = np.array(maturities)
        self.rates = np.array(rates)

        # Calibration des paramètres
        self.beta0, self.beta1, self.beta2, self.beta3, self.tau1, self.tau2 = self._calibrate()

    @staticmethod
    def _svensson(t, beta0, beta1, beta2, beta3, tau1, tau2):
        term1 = beta1 * (1 - np.exp(-t / tau1)) / (t / tau1)
        term2 = beta2 * ((1 - np.exp(-t / tau1)) / (t / tau1) - np.exp(-t / tau1))
        term3 = beta3 * ((1 - np.exp(-t / tau2)) / (t / tau2) - np.exp(-t / tau2))
        return beta0 + term1 + term2 + term3

    def _calibrate(self):
        p0 = [0.02, -0.02, 0.02, 0.01, 1.0, 2.0]  # Valeurs initiales
        bounds = ([0, -np.inf, -np.inf, -np.inf, 0.01, 0.01], [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf])
        params, _ = curve_fit(self._svensson, self.maturities, self.rates, p0=p0, bounds=bounds)
        return params

    def interpolate(self, t):
        return self._svensson(t, self.beta0, self.beta1, self.beta2, self.beta3, self.tau1, self.tau2)
