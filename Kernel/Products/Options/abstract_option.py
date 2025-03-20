from ..abstract_derive import AbstractDerive
import numpy as np

class AbstractOption(AbstractDerive):
    """
    Classe abstraite représentant les différentes options.
    """
    def __init__(self, maturity: float, strike: float = None):
        if maturity <= 0:
            raise ValueError("La maturité doit être positive.")
        self.maturity = maturity
        self.strike = strike
    
    def payoff(self, path : np.ndarray) -> float:
        """
        Calcule le payoff de l'option en fonction du chemin des prix ou des valeurs sous-jacentes.
        
        Args:
            path (np.ndarray): Liste ou tableau représentant le chemin des prix ou des
                valeurs sous-jacentes nécessaires pour calculer le payoff.
        Returns:
            float:  Le payoff de l'option.
        """
        pass