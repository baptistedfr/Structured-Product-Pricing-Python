from .abstract_option import AbstractOption
import numpy as np

class AbstractBinaryOption(AbstractOption):
    """
    Classe abstraite représentant les différentes options binaires.
    """
    def __init__(self, maturity : float, strike : float, coupon : float):
        """
        Initialise une option binaire avec une maturity, un prix d'exercice et un coupon.   "
        """
        super().__init__(maturity, strike)
        self.coupon = coupon
   

class BinaryCallOption(AbstractBinaryOption):
    """
    Classe représentant une option binaire d'achat (call).
    """
    
    def payoff(self, path : np.ndarray) -> float:
        """
        Calcule le payoff de l'option binaire d'achat (call).
        
        Args:
            path (np.ndarray): Liste ou tableau représentant le chemin des prix ou des
                valeurs sous-jacentes nécessaires pour calculer le payoff.
        Returns:
            float:  Le payoff de l'option binaire d'achat (call).
        """
        if path[-1] > self.strike:
            return self.coupon
        else:
            return 0
        
class BinaryPutOption(AbstractBinaryOption):
    """
    Classe représentant une option binaire de vente (put).
    """
    
    def payoff(self, path : np.ndarray) -> float:
        """
        Calcule le payoff de l'option binaire de vente (put).
        
        Args:
            path (np.ndarray): Liste ou tableau représentant le chemin des prix ou des
                valeurs sous-jacentes nécessaires pour calculer le payoff.
        Returns:
            float:  Le payoff de l'option binaire de vente (put).
        """
        if path[-1] < self.strike:
            return self.coupon
        else:
            return 0
    
