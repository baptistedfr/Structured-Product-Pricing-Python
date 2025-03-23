from enum import Enum
from . import EulerScheme, HestonEulerScheme

class EulerSchemeType(Enum):
    """
    Enum class representing the different types of Euler schemes.
    """
    EULER = EulerScheme
    HESTON_EULER = HestonEulerScheme