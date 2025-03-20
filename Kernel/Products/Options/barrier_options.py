import numpy as np
from .abstract_option import AbstractOption

class AbstractBarrierOption(AbstractOption):
    """
    Classe abstraite représentant les différentes options à barrière.
    """
    def __init__(self, maturity, strike, barrier):
        """
        Initialise une option à barrière avec une maturity, un prix d'exercice et une barrière.
        """
        super().__init__(maturity, strike)
        self.barrier = barrier
    
class UpBarrierOption(AbstractBarrierOption):
    """
    Classe abstraite pour les options avec barrière haute.
    """
    def __init__(self, maturity, strike, barrier):
        super().__init__(maturity, strike, barrier)
        if self.barrier <= self.strike:
            raise ValueError("La barrière doit être supérieure au strike pour une barrière haute.")

    def is_barrier_breached(self, path: np.ndarray) -> bool:
        """Vérifie si la barrière haute est franchie."""
        return np.max(path) > self.barrier

class DownBarrierOption(AbstractBarrierOption):
    """
    Classe abstraite pour les options avec barrière basse.
    """
    def __init__(self, maturity, strike, barrier):
        super().__init__(maturity, strike, barrier)
        if self.barrier >= self.strike:
            raise ValueError("La barrière doit être inférieure au strike pour une barrière basse.")

    def is_barrier_breached(self, path: np.ndarray) -> bool:
        """Vérifie si la barrière basse est franchie."""
        return np.min(path) < self.barrier

class UpAndOutCallOption(UpBarrierOption):
    """
    Classe représentant une option à barrière d'achat (call) avec barrière haute UpAndOut.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return 0
        return max(0, path[-1] - self.strike)

class UpAndInCallOption(UpBarrierOption):
    """
    Classe représentant une option à barrière d'achat (call) avec barrière haute Up And In.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return max(0, path[-1] - self.strike)
        return 0

class DownAndInCallOption(DownBarrierOption):
    """
    Classe représentant une option à barrière d'achat (call) avec barrière basse Down And In.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return max(0, path[-1] - self.strike)
        return 0

class DownAndOutCallOption(DownBarrierOption):
    """
    Classe représentant une option à barrière d'achat (call) avec barrière basse Down And Out.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return 0
        return max(0, path[-1] - self.strike)

class UpAndInPutOption(UpBarrierOption):
    """
    Classe représentant une option à barrière de vente (put) avec barrière haute Up And In.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return max(0, self.strike - path[-1])
        return 0

class UpAndOutPutOption(UpBarrierOption):
    """
    Classe représentant une option à barrière de vente (put) avec barrière haute Up And Out.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return 0
        return max(0, self.strike - path[-1])

class DownAndInPutOption(DownBarrierOption):
    """
    Classe représentant une option à barrière de vente (put) avec barrière basse Down And In.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return max(0, self.strike - path[-1])
        return 0

class DownAndOutPutOption(DownBarrierOption):
    """
    Classe représentant une option à barrière de vente (put) avec barrière basse Down And Out.
    """
    def payoff(self, path: np.ndarray) -> float:
        if self.is_barrier_breached(path):
            return 0
        return max(0, self.strike - path[-1])