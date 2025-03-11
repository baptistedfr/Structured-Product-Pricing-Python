from abc import ABC, abstractmethod

class Interpolator(ABC):

    @abstractmethod
    def interpolate(self, t):
        pass
