from abc import ABC, abstractmethod
import numpy as np
from scipy.interpolate import interp1d, CubicSpline

class Interpolator(ABC):

    @abstractmethod
    def interpolate(self, t):
        pass

class LinearInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        self.interpolator = interp1d(maturities, rates, kind='linear', fill_value="extrapolate")

    def interpolate(self, t):
        return self.interpolator(t)

class CubicInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        self.interpolator = CubicSpline(maturities, rates, bc_type='natural', extrapolate=True)

    def interpolate(self, t):
        return self.interpolator(t)

class NelsonSiegelInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        # Calib du NS
        self.beta0, self.beta1, self.beta2, self.tau = 0.02, -0.02, 0.02, 1.0

    def interpolate(self, t):
        return self.beta0 + self.beta1 * (1 - np.exp(-t / self.tau)) / (t / self.tau) + self.beta2 * ((1 - np.exp(-t / self.tau)) / (t / self.tau) - np.exp(-t / self.tau))

class StevensonInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        # Calib du NS
        ...

    def interpolate(self, t):
        ...