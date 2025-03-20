from typing import List, Tuple
import numpy as np
from ..abstract_derive import AbstractDerive
from ..options.abstract_option import AbstractOption

class AbstractOptionStrategy(AbstractDerive):
    """
    Classe représentant une stratégie optionnelle composée de plusieurs options.
    """
    def __init__(self, options: List[Tuple[AbstractOption, bool]] = None):
        """
        Initialise une stratégie optionnelle.

        Args:
            options (List[Tuple[AbstractOption, bool]]): Liste de tuples contenant une option et un booléen
                indiquant si l'option est achetée (True) ou vendue (False).
        """
        self.options: List[Tuple[AbstractOption, bool]] = options if options is not None else []

    def add_option(self, option: AbstractOption, is_long: bool):
        """
        Ajoute une option à la stratégie.

        Args:
            option (AbstractOption): Une instance d'option à ajouter.
            is_long (bool): Indique si l'option est achetée (True) ou vendue (False).
        """
        self.options.append((option, is_long))

    def payoff(self, path: np.ndarray) -> np.ndarray:
        """
        Calcule le payoff total de la stratégie pour un chemin donné.

        Args:
            path (np.ndarray): Chemin des prix ou des valeurs sous-jacentes.

        Returns:
            np.ndarray: Le payoff total de la stratégie pour chaque point du chemin.
        """
        total_payoff = 0
        for option, is_long in self.options:
            payoff = option.payoff(path)
            total_payoff += payoff if is_long else -payoff
        return total_payoff

    def __str__(self) -> str:
        """
        Représentation textuelle de la stratégie.

        Returns:
            str: Description de la stratégie et des options qu'elle contient.
        """
        return f"AbstractOptionStrategy avec {len(self.options)} options: " + \
               f"{[(str(option), is_long) for option, is_long in self.options]}"
