import numpy as np
from scipy.stats import norm

class EulerScheme:
    @staticmethod
    def simulate_paths(process, seed, nb_paths):  # voir pour l'ajout des dividendes discrets ou alors on fait que continu
        increments = process.get_increments(seed, nb_paths)
        paths = np.zeros((nb_paths, process.nb_steps + 1))
        paths[:, 0] = process.initial_value
        factors = process.drift * process.dt + process.diffusion * increments
        paths[:, 1:] = process.initial_value * np.cumprod(1 + factors, axis=1)
        return paths

