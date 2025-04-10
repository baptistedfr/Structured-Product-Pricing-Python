from kernel.products.options.abstract_option import AbstractOption
import numpy as np
from abc import ABC, abstractmethod
from typing import Union, List

class AmericanAbstractOption(AbstractOption):
    """
    Classe représentant une option américaine.
    """
    def __init__(self, strike: float, maturity: float) -> None:
        super().__init__(strike=strike, maturity=maturity)
        self.exercise_times = None

    def payoff(self, path: np.ndarray) -> float:
        pass

    @abstractmethod
    def instrinsec_payoff(self, S: np.ndarray)-> np.ndarray:
        pass
    
class AmericanCallOption(AmericanAbstractOption):

    def __init__(self, strike:float, maturity:float):
        super().__init__(strike=strike, maturity=maturity)

    def instrinsec_payoff(self, S):
        return np.maximum(S - self.strike, 0)
    
class AmericanPutOption(AmericanAbstractOption):

    def __init__(self, strike:float, maturity:float):
        super().__init__(strike=strike, maturity=maturity)

    def instrinsec_payoff(self, S:np.ndarray):
        return np.maximum(self.strike - S, 0)

class BermudeanCallOption(AmericanCallOption):

    def __init__(self, strike, maturity, exercise_times):
        super().__init__(strike=strike, maturity=maturity)
        self.exercise_times = exercise_times

class BermudeanPutOption(AmericanPutOption):
    def __init__(self, strike:float, maturity:float, exercise_times:List[float]):
        super().__init__(strike=strike, maturity=maturity)
        self.exercise_times = exercise_times