from kernel.models.stochastic_processes.black_scholes_process import BlackScholesProcess
from kernel.models.discritization_schemes.euler_scheme import EulerScheme
import numpy as np 


T=1
nb_steps=25
dt=T/nb_steps
r=0.05
sigma=0.2
initial_value=110

bs_process = BlackScholesProcess(initial_value, dt, nb_steps, sigma, r)
seed=123
nb_paths=200000
paths=EulerScheme.simulate_paths(bs_process, seed, nb_paths)

strike =100
payoff = np.maximum(paths[:,-1]-strike,0)
price = np.mean(payoff)*np.exp(-r*T)
print(price)
# Expected output: 8.021