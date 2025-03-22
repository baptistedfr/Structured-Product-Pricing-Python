from kernel.models.stochastic_processes.stochastic_process import StochasticProcess

class BlackScholesProcess(StochasticProcess):
    """
    Class representing a Black-Scholes process.
    Inherits from StochasticProcess.
    """

    def __init__(self, S0: float, T: float, nb_steps: int, drift: float, volatility: float):
        """
        Initializes the stochastic process.

        Parameters:
            S0 (float): The initial value of the process
            T (float): The maturity of the process
            nb_steps (int): The number of steps to simulate
        """
        super().__init__(S0, T, nb_steps)
        self.drift = drift
        self.diffusion = volatility 
