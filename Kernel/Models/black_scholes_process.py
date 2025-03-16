from stochastic_process import StochasticProcess

class BlackScholesProcess(StochasticProcess):
    def __init__(self, initial_value, dt, nb_steps, volatility, drift):
        super().__init__(initial_value, dt, nb_steps)
        self.drift = drift
        self.diffusion = volatility 
