import numpy as np
from .abstract_option import AbstractOption

class AsianCallOption(AbstractOption):
    """
    Option asiatique call où le payoff dépend de la moyenne des prix du sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff de l'option asiatique call.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option asiatique call.
        """
        average_price = np.mean(path)  # Moyenne des prix
        return max(0, average_price - self.strike)  


class AsianPutOption(AbstractOption):
    """
    Option asiatique put où le payoff dépend de la moyenne des prix du sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff de l'option asiatique put.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option asiatique put.
        """
        average_price = np.mean(path)  # Moyenne des prix
        return max(0, self.strike - average_price)  


class LookbackCallOption(AbstractOption):
    """
    Option lookback call où le payoff dépend du prix maximum atteint par le sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff de l'option lookback call.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option lookback call.
        """
        max_price = np.max(path)  # Prix maximum atteint
        return max(0, max_price - self.strike)  


class LookbackPutOption(AbstractOption):
    """
    Option lookback put où le payoff dépend du prix minimum atteint par le sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff de l'option lookback put.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option lookback put.
        """
        min_price = np.min(path)  # Prix minimum atteint
        return max(0, self.strike - min_price)  

class FloatingStrikeCallOption(AbstractOption):
    """
    Option call à strike flottant où le strike est basé sur la moyenne des prix du sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff d'une option call à strike flottant.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option call à strike flottant.
        """
        floating_strike = np.mean(path)  # Strike basé sur la moyenne des prix
        return max(0, path[-1] - floating_strike)  # Payoff pour un call


class FloatingStrikePutOption(AbstractOption):
    """
    Option put à strike flottant où le strike est basé sur la moyenne des prix du sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff d'une option put à strike flottant.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option put à strike flottant.
        """
        floating_strike = np.mean(path)  # Strike basé sur la moyenne des prix
        return max(0, floating_strike - path[-1])  # Payoff pour un put
    
class ForwardStartCallOption(AbstractOption):
    """
    Option call forward start où le strike est basé sur le premier prix du sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff d'une option call forward start.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option call forward start.
        """
        forward_start_strike = path[0]  # Exemple : strike basé sur le premier prix
        return max(0, path[-1] - forward_start_strike)  # Payoff pour un call


class ForwardStartPutOption(AbstractOption):
    """
    Option put forward start où le strike est basé sur le premier prix du sous-jacent.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff d'une option put forward start.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option put forward start.
        """
        forward_start_strike = path[0]  # Exemple : strike basé sur le premier prix
        return max(0, forward_start_strike - path[-1])  # Payoff pour un put
    
class ChooserOption(AbstractOption):
    """
    Option chooser qui permet de choisir entre un call et un put à l'échéance.
    """
    def payoff(self, path: np.ndarray) -> float:
        """
        Calcule le payoff d'une option chooser.

        Args:
            path (np.ndarray): Chemin des prix du sous-jacent.

        Returns:
            float: Le payoff de l'option chooser.
        """
        call_payoff = max(0, path[-1] - self.strike)  # Payoff pour un call
        put_payoff = max(0, self.strike - path[-1])  # Payoff pour un put
        return max(call_payoff, put_payoff)  # Choix du meilleur payoff