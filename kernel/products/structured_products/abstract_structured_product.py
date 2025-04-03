from abc import ABC, abstractmethod
import numpy as np

class AbstractStructuredProduct(ABC):
    """
    Classe abstraite représentant un produit structuré.
    """
    def __init__(self, maturity : float):
        self.validate_inputs(maturity)
        self.maturity = maturity

    def validate_inputs(self, maturity : float):
        """
        Valide les entrées pour la maturité et le nominal.

        Args:
            maturity (float): La maturité du produit structuré.
            notional (float): Le nominal du produit structuré.

        Raises:
            ValueError: Si la maturité ou le nominal ne sont pas positifs.
        """
        if maturity <= 0:
            raise ValueError("La maturité doit être positive.")

    @abstractmethod
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff du produit structuré.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff du produit structuré.
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """
        Retourne une description textuelle du produit structuré.

        Returns:
            str: Description du produit structuré.
        """
        pass