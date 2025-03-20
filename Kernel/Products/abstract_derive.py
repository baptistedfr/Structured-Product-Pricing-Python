from abc import ABC, abstractmethod
import numpy as np 

class AbstractDerive(ABC):
    """
    Classe abstraite représentant les différents dérivés.
    """
    @abstractmethod
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff du dérivé en fonction du chemin des prix ou des valeurs sous-jacentes.

        Args:
            path (np.ndarray): Liste ou tableau représentant le chemin des prix ou des
                valeurs sous-jacentes nécessaires pour calculer le payoff.
        Returns:
            float:  Le payoff du dérivé.
        """
        pass