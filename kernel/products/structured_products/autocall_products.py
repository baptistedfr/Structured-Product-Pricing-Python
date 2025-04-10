from abc import ABC, abstractmethod
import numpy as np
from ...tools import ObservationFrequency
from . import AbstractStructuredProduct

class AbstractAutocall(AbstractStructuredProduct):
    """
    Classe abstraite pour les produits Autocall.

    Attributs :
        maturity (float) : Maturité du produit en années.
        observation_frequency (ObservationFrequency) : Fréquence des observations.
        capital_barrier (float) : Niveau de protection du capital.
        autocall_barrier (float) : Niveau de rappel anticipé (autocall).
        coupon_rate (float) : Taux du coupon.
        is_security (bool) : Protection améliorée en cas de perte.
        is_plus (bool) : Option "Plus" qui cumule les coupons non versés.
    """
    def __init__(self, maturity: float, observation_frequency: ObservationFrequency,  
                 capital_barrier: float, autocall_barrier: float, coupon_rate: float, 
                 is_security: bool = False, is_plus: bool = False):
        
        super().__init__(maturity)
        self.observation_frequency = observation_frequency
        self.capital_barrier = capital_barrier
        self.autocall_barrier = autocall_barrier
        self.coupon_rate = coupon_rate
        self.is_security = is_security
        self.is_plus = is_plus

    @abstractmethod
    def payoff(self, paths: np.ndarray) -> float:
        pass


class Phoenix(AbstractAutocall):
    """
    Produit Phoenix : verse des coupons périodiques si le sous-jacent est au-dessus d'une barrière.
    - Peut être rappelé automatiquement si le sous-jacent dépasse une barrière donnée.
    - À maturité, protection du capital sous certaines conditions.
    """
    def __init__(self, maturity, observation_frequency, 
                 capital_barrier, autocall_barrier, 
                 coupon_rate, coupon_barrier,
                 is_security=False, is_plus=False):
        
        super().__init__(maturity, observation_frequency, capital_barrier, autocall_barrier, coupon_rate, is_security, is_plus)
        self.coupon_barrier = coupon_barrier
    
    def payoff(self, paths: np.ndarray) -> float:

        index_observations = np.linspace(0, len(paths) - 1, int((self.maturity * self.observation_frequency.value) + 1)).astype(int)
        num_observations = len(index_observations)
        paths = (paths[index_observations]/paths[0])*100
        coupons = 0
        missed_coupons = 0

        for t in range(1, num_observations):
            if paths[t] >= self.autocall_barrier:
                return 100 + coupons + self.coupon_rate + missed_coupons, t  # Rappel automatique

            if paths[t] >= self.coupon_barrier:
                coupons += self.coupon_rate + missed_coupons
                missed_coupons = 0  # Remise à zéro des coupons manqués
            else:
                if self.is_plus:
                    missed_coupons += self.coupon_rate  # Cumule les coupons si "Plus"

        # À maturité (t = num_observations - 1)
        final_price = paths[-1]
        if final_price >= self.capital_barrier:
            return 100 + coupons + missed_coupons, num_observations
        else:
            if self.is_security:
                gearing = 100 / self.capital_barrier
                loss = (self.capital_barrier - final_price) * gearing 
                return max(0, 100 - loss + coupons), num_observations
            else:
                return max(0, final_price + coupons), num_observations


class Eagle(AbstractAutocall):
    """
    Produit Eagle : variation du Phoenix avec une approche différente des coupons.
    - Peut être rappelé automatiquement si la barrière d’autocall est franchie.
    - Protection du capital sous conditions.
    """
    def __init__(self, maturity, observation_frequency, 
                 capital_barrier, autocall_barrier, 
                 coupon_rate,
                 is_security=False, is_plus=False):
        
        super().__init__(maturity, observation_frequency, capital_barrier, autocall_barrier, coupon_rate, is_security, is_plus)
    
    def payoff(self, paths: np.ndarray) -> float:
        index_observations = np.linspace(0, len(paths) - 1, int((self.maturity * self.observation_frequency.value) + 1)).astype(int)
        num_observations = len(index_observations)
        paths = (paths[index_observations]/paths[0])*100

        for t in range(1, num_observations):
            if paths[t] >= self.autocall_barrier:
                return 100 + t * self.coupon_rate, t  # Rappel automatique avec paiement des coupons

        # À maturité
        final_price = paths[-1]
        if final_price >= self.capital_barrier:
            return 100 + num_observations * self.coupon_rate if self.is_plus else 100, num_observations
        else:
            if self.is_security:
                gearing = 100 / self.capital_barrier
                loss = (self.capital_barrier - final_price) * gearing 
                return max(0, 100 - loss), num_observations
            else:
                return max(0, final_price), num_observations