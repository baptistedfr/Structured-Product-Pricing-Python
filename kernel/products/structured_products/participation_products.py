import numpy as np
from .abstract_structured_product import AbstractStructuredProduct

class AbstractParticipationProduct(AbstractStructuredProduct):
    """
    Classe abstraite pour les produits de participation.
    """
    def __init__(self, maturity: float, rebate: float, leverage: float):
        """
        Initialise un produit de participation.

        Args:
            maturity (float): Maturité du produit.
            notional (float): Nominal du produit.
            rebate (float, optional): Remboursement fixe en cas de conditions spécifiques. Par défaut, 0.
            leverage (float, optional): Facteur de levier pour amplifier les gains ou pertes. Par défaut, 1.
        """
        super().__init__(maturity)
        self.rebate: float = rebate
        self.leverage: float = leverage

class TwinWin(AbstractParticipationProduct):
    """
    Produit structuré Twin Win avec barrières supérieure et inférieure, rebate et levier.
    """
    def __init__(self, maturity: float, upper_barrier: float, lower_barrier: float, rebate: float = 0, leverage: float = 100):
        """
        Initialise un produit Twin Win.

        Args:
            maturity (float): Maturité du produit.
            upper_barrier (float): Barrière supérieure.
            lower_barrier (float): Barrière inférieure.
            rebate (float, optional): Remboursement fixe si la barrière supérieure est franchie. Par défaut, 0.
            leverage (float, optional): Facteur de levier. Par défaut, 1.
        """
        super().__init__(maturity = maturity, rebate=rebate, leverage=leverage)
        if upper_barrier <= lower_barrier:
            raise ValueError("La barrière supérieure doit être strictement supérieure à la barrière inférieure.")
        self.upper_barrier = upper_barrier
        self.lower_barrier = lower_barrier

    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff du Twin Win.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff du Twin Win.
        """
        final_price: float = paths[-1] # Prix final du sous-jacent
        initial_price : float = paths[0]  # Prix inital du sous-jacent
        performance: float = (final_price / initial_price) * 100
        payoff = 100
        # Si la barrière supérieure est franchie
        if performance > self.upper_barrier:
            payoff = 100 + self.rebate  # Remboursement fixe
        # Si la barrière inférieure est franchie
        elif performance < self.lower_barrier:
            # Perte similaire à un Put Down-and-In
            loss = self.leverage * (performance - 100)
            payoff =  100 + loss  # Perte
        else:
            # Participation dans la plage définie par les barrières
            payoff = self.leverage * abs(performance - 100) + 100
        print(payoff)
        return payoff

    def description(self) -> str:
        if self.upper_barrier:
            return (f"Twin Win avec barrière supérieure à {self.upper_barrier}, barrière inférieure à {self.lower_barrier}, "
                     "rebate de {self.rebate}, et levier de {self.leverage}.")
        else:
            return (f"Twin Win sans barrière supérieure capante, barrière inférieure à {self.lower_barrier}, "
                    f"rebate de {self.rebate}, et levier de {self.leverage}.")
    

class Airbag(AbstractParticipationProduct):
    """
    Produit structuré AirBag avec barrières supérieure et inférieure, rebate et levier.
    """
    def __init__(self, maturity: float, upper_barrier: float, lower_barrier: float, rebate: float = 0, leverage: float = 1):
        """
        Initialise un produit AirBag.

        Args:
            maturity (float): Maturité du produit.
            notional (float): Nominal du produit.
            upper_barrier (float): Barrière supérieure.
            lower_barrier (float): Barrière inférieure.
            rebate (float, optional): Remboursement fixe si la barrière supérieure est franchie. Par défaut, 0.
            leverage (float, optional): Facteur de levier. Par défaut, 1.
        """
        super().__init__(maturity = maturity, rebate=rebate, leverage=leverage)
        if upper_barrier <= lower_barrier:
            raise ValueError("La barrière supérieure doit être strictement supérieure à la barrière inférieure.")
        self.upper_barrier = upper_barrier
        self.lower_barrier = lower_barrier

    def payoff(self, paths: np.ndarray) -> float:
        """
        Calcule le payoff du Airbag.

        Args:
            paths (np.ndarray): Chemins des prix des sous-jacents.

        Returns:
            float: Le payoff du Airbag.
        """
        final_price: float = paths[-1]  # Prix final du sous-jacent
        initial_price: float = paths[0]
        performance: float =  (final_price / initial_price) * 100
        payoff = 100
        # Si la barrière supérieure est franchie
        if performance > self.upper_barrier:
            payoff =  100 + self.rebate  # Remboursement fixe
        # Si la barrière inférieure est franchie
        elif performance < self.lower_barrier:
            # Perte similaire à un Put Down-and-In
            loss = self.leverage  * (performance - 100)
            payoff = loss + 100  # Perte
        elif performance < 100:
            payoff =  100
        else:
            # Participation dans la plage définie par les barrières
            payoff = self.leverage * (performance - 100) + 100

        return payoff

    def description(self) -> str:
        if self.upper_barrier:
            return (f"Airbag avec barrière supérieure à {self.upper_barrier}, barrière inférieure à {self.lower_barrier}, "
                    f"rebate de {self.rebate}, et levier de {self.leverage}.")
        else:
            return (f"Airbag sans barrière supérieure capante, barrière inférieure à {self.lower_barrier}, "
                    f"rebate de {self.rebate}, et levier de {self.leverage}.")