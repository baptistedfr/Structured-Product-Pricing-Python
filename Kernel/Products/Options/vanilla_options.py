from .abstract_option import AbstractOption
import numpy as np

class CallOption(AbstractOption):
    """
    Classe représentant une option d'achat (call).
    """
    def payoff(self, path : np.ndarray) -> float:
        """
        Calcule le payoff de l'option d'achat (call).
        
        Args:
            path (np.ndarray): Liste ou tableau représentant le chemin des prix ou des
                valeurs sous-jacentes nécessaires pour calculer le payoff.
        Returns:
            float:  Le payoff de l'option d'achat (call).
        """
        return max(0, path[-1] - self.strike)

class PutOption(AbstractOption):
    """
    Classe représentant une option de vente (put).
    """
    def payoff(self, path : np.ndarray) -> float:
        """
        Calcule le payoff de l'option de vente (put).
        
        Args:
            path (np.ndarray): Liste ou tableau représentant le chemin des prix ou des
                valeurs sous-jacentes nécessaires pour calculer le payoff.
        Returns:
            float:  Le payoff de l'option de vente (put).
        """
        return max(0, self.strike - path[-1])
    
    