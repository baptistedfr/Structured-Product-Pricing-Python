from .abstract_option import AbstractOption
import numpy as np

class AbstractMultiAssetOption(AbstractOption):
    """
    Classe abstraite pour les options avec plusieurs sous-jacents.
    """
    def __init__(self, maturity, strike, weights=None):
        """
        Initialise une option multi-sous-jacent.

        Args:
            maturity (float): Maturité de l'option.
            strike (float): Prix d'exercice de l'option.
            weights (np.ndarray, optional): Poids des sous-jacents. Par défaut, poids égaux.
        """
        super().__init__(maturity, strike)
        self.weights = weights

    def weighted_average(self, paths: np.ndarray) -> float:
        """
        Calcule la moyenne pondérée des sous-jacents.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Moyenne pondérée des sous-jacents.
        """
        if self.weights is None:
            self.weights = np.ones(paths.shape[0]) / paths.shape[0]  # Poids égaux par défaut
        return np.dot(self.weights, paths)
    
class BasketCallOption(AbstractMultiAssetOption):
    """
    Classe représentant une option basket avec des poids fixes pour une option d'achat.
    """
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff de l'option basket.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff de l'option basket.
        """
        basket_price = self.weighted_average(paths[:, -1])  # Moyenne pondérée des prix finaux
        return max(0, basket_price - self.strike)  # Payoff pour un call
    
class BasketPutOption(AbstractMultiAssetOption):
    """
    Classe représentant une option basket avec des poids fixes pour une option de vente.
    """
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff de l'option basket.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff de l'option basket.
        """
        basket_price = self.weighted_average(paths[:, -1])  # Moyenne pondérée des prix finaux
        return max(0, self.strike - basket_price)  # Payoff pour un call

class BestOfCallOption(AbstractMultiAssetOption):
    """
    Classe représentant une option Best-Of Call.
    Le payoff est basé sur le meilleur sous-jacent à la date finale.
    """
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff de l'option Best-Of Call.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff de l'option Best-Of Call.
        """
        best_performance = np.max(paths[:, -1])  # Meilleur prix final parmi les sous-jacents
        return max(0, best_performance - self.strike)  # Payoff pour un call


class BestOfPutOption(AbstractMultiAssetOption):
    """
    Classe représentant une option Best-Of Put.
    Le payoff est basé sur le meilleur sous-jacent à la date finale.
    """
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff de l'option Best-Of Put.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff de l'option Best-Of Put.
        """
        best_performance = np.max(paths[:, -1])  # Meilleur prix final parmi les sous-jacents
        return max(0, self.strike - best_performance)  # Payoff pour un put


class WorstOfCallOption(AbstractMultiAssetOption):
    """
    Classe représentant une option Worst-Of Call.
    Le payoff est basé sur le pire sous-jacent à la date finale.
    """
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff de l'option Worst-Of Call.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff de l'option Worst-Of Call.
        """
        worst_performance = np.min(paths[:, -1])  # Pire prix final parmi les sous-jacents
        return max(0, worst_performance - self.strike)  # Payoff pour un call


class WorstOfPutOption(AbstractMultiAssetOption):
    """
    Classe représentant une option Worst-Of Put.
    Le payoff est basé sur le pire sous-jacent à la date finale.
    """
    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff de l'option Worst-Of Put.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff de l'option Worst-Of Put.
        """
        worst_performance = np.min(paths[:, -1])  # Pire prix final parmi les sous-jacents
        return max(0, self.strike - worst_performance)  # Payoff pour un put