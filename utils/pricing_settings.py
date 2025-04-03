from datetime import datetime
from typing import Optional
from kernel.models.discritization_schemes import AbstractScheme

class PricingSettings:
    def __init__(self):
        self.day_count_convention: Optional[str] = None
        self.nb_paths: Optional[int] = None
        self.nb_steps: Optional[int] = None
        self.valuation_date: Optional[datetime] = None
        self.compute_greeks: bool = False
        self.random_seed: Optional[int] = None
        self.model: Optional[str] = None  # a voir
        self.discretization_scheme: Optional["AbstractScheme"] = None
