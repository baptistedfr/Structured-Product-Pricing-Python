from .abstract_option import AbstractOption
import numpy as np

class EuropeanCallOption(AbstractOption):
    """
    Classe représentant une option d'achat (call) européenne.
    """
    def payoff(self, path : np.ndarray) -> float:
        return max(0, path[-1] - self.strike)

class EuropeanPutOption(AbstractOption):
    """
    Classe représentant une option de vente (put) européenne.
    """
    def payoff(self, path : np.ndarray) -> float:
        return max(0, self.strike - path[-1])
