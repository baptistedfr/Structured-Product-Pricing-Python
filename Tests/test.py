import unittest
import numpy as np
from Kernel.Products import *


class TestBarrierOptions(unittest.TestCase):
    def setUp(self):
        # Initialisation des paramètres communs
        self.maturity = 1.0
        self.strike = 100
        self.barrier_up = 110  # Barrière supérieure
        self.barrier_down = 90  # Barrière inférieure
        self.path_below_barrier_up = np.array([90, 95, 100, 105])  # Chemin qui ne franchit pas la barrière supérieure
        self.path_above_barrier_up = np.array([90, 95, 110, 115])  # Chemin qui franchit la barrière supérieure
        self.path_below_barrier_down = np.array([120, 115, 110, 105])  # Chemin qui ne franchit pas la barrière inférieure
        self.path_above_barrier_down = np.array([120, 115, 100, 85])  # Chemin qui franchit la barrière inférieure

    def test_up_and_out_call_option(self):
        option = UpAndOutCallOption(self.maturity, self.strike, self.barrier_up)
        self.assertEqual(option.payoff(self.path_below_barrier_up), max(0, self.path_below_barrier_up[-1] - self.strike))
        self.assertEqual(option.payoff(self.path_above_barrier_up), 0)

    def test_up_and_in_call_option(self):
        option = UpAndInCallOption(self.maturity, self.strike, self.barrier_up)
        self.assertEqual(option.payoff(self.path_below_barrier_up), 0)
        self.assertEqual(option.payoff(self.path_above_barrier_up), max(0, self.path_above_barrier_up[-1] - self.strike))

    def test_down_and_in_call_option(self):
        option = DownAndInCallOption(self.maturity, self.strike, self.barrier_down)
        self.assertEqual(option.payoff(self.path_below_barrier_down), 0)
        self.assertEqual(option.payoff(self.path_above_barrier_down), max(0, self.path_above_barrier_down[-1] - self.strike))

    def test_down_and_out_call_option(self):
        option = DownAndOutCallOption(self.maturity, self.strike, self.barrier_down)
        self.assertEqual(option.payoff(self.path_below_barrier_down), max(0, self.path_below_barrier_down[-1] - self.strike))
        self.assertEqual(option.payoff(self.path_above_barrier_down), 0)

    def test_up_and_in_put_option(self):
        option = UpAndInPutOption(self.maturity, self.strike, self.barrier_up)
        self.assertEqual(option.payoff(self.path_below_barrier_up), 0)
        self.assertEqual(option.payoff(self.path_above_barrier_up), max(0, self.strike - self.path_above_barrier_up[-1]))

    def test_up_and_out_put_option(self):
        option = UpAndOutPutOption(self.maturity, self.strike, self.barrier_up)
        self.assertEqual(option.payoff(self.path_below_barrier_up), max(0, self.strike - self.path_below_barrier_up[-1]))
        self.assertEqual(option.payoff(self.path_above_barrier_up), 0)

    def test_down_and_in_put_option(self):
        option = DownAndInPutOption(self.maturity, self.strike, self.barrier_down)
        self.assertEqual(option.payoff(self.path_below_barrier_down), 0)
        self.assertEqual(option.payoff(self.path_above_barrier_down), max(0, self.strike - self.path_above_barrier_down[-1]))

    def test_down_and_out_put_option(self):
        option = DownAndOutPutOption(self.maturity, self.strike, self.barrier_down)
        self.assertEqual(option.payoff(self.path_below_barrier_down), max(0, self.strike - self.path_below_barrier_down[-1]))
        self.assertEqual(option.payoff(self.path_above_barrier_down), 0)
        
class TestCallPutOptions(unittest.TestCase):
    def setUp(self):
        # Initialisation des paramètres communs
        self.maturity = 1.0
        self.strike = 100
        self.coupon = 1
        self.path_above_strike = np.array([90, 95, 100, 105])  # Chemin où le prix final est au-dessus du strike
        self.path_below_strike = np.array([90, 95, 100, 95])   # Chemin où le prix final est en dessous du strike

    def test_european_call_option(self):
        option = CallOption(self.maturity, self.strike)
        self.assertEqual(option.payoff(self.path_above_strike), max(0, self.path_above_strike[-1] - self.strike))
        self.assertEqual(option.payoff(self.path_below_strike), 0)

    def test_european_put_option(self):
        option = PutOption(self.maturity, self.strike)
        self.assertEqual(option.payoff(self.path_above_strike), 0)
        self.assertEqual(option.payoff(self.path_below_strike), max(0, self.strike - self.path_below_strike[-1]))

    def test_binary_call_option(self):
        option = BinaryCallOption(self.maturity, self.strike, self.coupon)
        self.assertEqual(option.payoff(self.path_above_strike), self.coupon)  # Payoff = 1 si le prix final est au-dessus du strike
        self.assertEqual(option.payoff(self.path_below_strike), 0)  # Payoff = 0 sinon

    def test_binary_put_option(self):
        option = BinaryPutOption(self.maturity, self.strike, self.coupon)
        self.assertEqual(option.payoff(self.path_above_strike), 0)  # Payoff = 0 si le prix final est au-dessus du strike
        self.assertEqual(option.payoff(self.path_below_strike), self.coupon)  # Payoff = 1 sinon

if __name__ == "__main__":
    unittest.main()