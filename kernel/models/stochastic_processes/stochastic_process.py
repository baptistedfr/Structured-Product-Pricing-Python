from abc import ABC, abstractmethod
import random
import numpy as np
from scipy.stats import norm
from enum import Enum


class StochasticProcess(ABC):
    def __init__(self, initial_value, T, nb_steps):
        dt = T/nb_steps
        if dt <= 0:
            raise ValueError("Le temps (dt) doit être positif.")
        if nb_steps <= 0:
            raise ValueError("Le nombre de pas doit être positif.")
        self.initial_value = initial_value
        self.nb_steps = nb_steps
        self.T = T
        self.dt = dt
        self.drift = None
        self.diffusion = None

    def get_brownian_increments(self,seed,nb_paths):
        rng = np.random.default_rng(seed)
        random_unif = rng.uniform(0, 1, size=(nb_paths, self.nb_steps))
        increments = norm.ppf(random_unif) * np.sqrt(self.dt)
        return increments
