from enum import Enum
from ..volatility_surface import SVIVolatilitySurface, LocalVolatilitySurface

class VolatilitySurfaceType(Enum):
    LOCAL = LocalVolatilitySurface
    SVI = SVIVolatilitySurface

