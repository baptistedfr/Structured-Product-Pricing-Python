from enum import Enum
from ..volatility_surface import *

class VolatilitySurfaceType(Enum):
    LOCAL = LocalVolatilitySurface
    SVI = SVIVolatilitySurface
    SSVI = SSVIVolatilitySurface
