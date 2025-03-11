from .abstract_interpolator import Interpolator
from scipy.interpolate import CubicSpline

class CubicInterpolator(Interpolator):

    def __init__(self, maturities, rates):
        self.interpolator = CubicSpline(maturities, rates, bc_type='natural', extrapolate=True)

    def interpolate(self, t):
        return self.interpolator(t)