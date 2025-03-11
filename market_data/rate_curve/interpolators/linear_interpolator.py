from .abstract_interpolator import Interpolator
from scipy.interpolate import interp1d

class LinearInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        self.interpolator = interp1d(maturities, rates, kind='linear', fill_value="extrapolate")

    def interpolate(self, t):
        return self.interpolator(t)