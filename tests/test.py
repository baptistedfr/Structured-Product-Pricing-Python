import unittest
import numpy as np
from kernel.products import *


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
        option = EuropeanCallOption(self.maturity, self.strike)
        self.assertEqual(option.payoff(self.path_above_strike), max(0, self.path_above_strike[-1] - self.strike))
        self.assertEqual(option.payoff(self.path_below_strike), 0)

    def test_european_put_option(self):
        option = EuropeanPutOption(self.maturity, self.strike)
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

class TestPathDependantOptions(unittest.TestCase):
    def setUp(self):
        # Initialisation des paramètres communs
        self.maturity = 1.0
        self.strike = 100
        self.path = np.array([90, 95, 100, 105, 110])  # Exemple de chemin

    def test_asian_call_option(self):
        option = AsianCallOption(self.maturity, self.strike)
        average_price = np.mean(self.path)
        expected_payoff = max(0, average_price - self.strike)
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_asian_put_option(self):
        option = AsianPutOption(self.maturity, self.strike)
        average_price = np.mean(self.path)
        expected_payoff = max(0, self.strike - average_price)
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_lookback_call_option(self):
        option = LookbackCallOption(self.maturity, self.strike)
        max_price = np.max(self.path)
        expected_payoff = max(0, max_price - self.strike)
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_lookback_put_option(self):
        option = LookbackPutOption(self.maturity, self.strike)
        min_price = np.min(self.path)
        expected_payoff = max(0, self.strike - min_price)
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_floating_strike_call_option(self):
        option = FloatingStrikeCallOption(self.maturity, self.strike)
        floating_strike = np.mean(self.path)
        expected_payoff = max(0, self.path[-1] - floating_strike)
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_floating_strike_put_option(self):
        option = FloatingStrikePutOption(self.maturity, self.strike)
        floating_strike = np.mean(self.path)
        expected_payoff = max(0, floating_strike - self.path[-1])
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_forward_start_call_option(self):
        option = ForwardStartCallOption(self.maturity, self.strike)
        forward_start_strike = self.path[0]  # Strike basé sur le premier prix
        expected_payoff = max(0, self.path[-1] - forward_start_strike)
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_forward_start_put_option(self):
        option = ForwardStartPutOption(self.maturity, self.strike)
        forward_start_strike = self.path[0]  # Strike basé sur le premier prix
        expected_payoff = max(0, forward_start_strike - self.path[-1])
        self.assertEqual(option.payoff(self.path), expected_payoff)

    def test_chooser_option(self):
        option = ChooserOption(self.maturity, self.strike)
        call_payoff = max(0, self.path[-1] - self.strike)
        put_payoff = max(0, self.strike - self.path[-1])
        expected_payoff = max(call_payoff, put_payoff)  # Choix du meilleur payoff
        self.assertEqual(option.payoff(self.path), expected_payoff)

class TestMultiAssetOptions(unittest.TestCase):
    def setUp(self):
        # Initialisation des paramètres communs
        self.maturity = 1.0
        self.strike = 100
        # Exemple de chemins pour 3 sous-jacents
        self.paths = np.array([
            [90, 95, 100, 105],  # Sous-jacent 1
            [80, 85, 90, 95],    # Sous-jacent 2
            [110, 115, 120, 125] # Sous-jacent 3
        ])
        # Poids pour BasketOption
        self.weights = np.array([0.5, 0.3, 0.2])

    def test_basket_call_option(self):
        option = BasketCallOption(self.maturity, self.strike, weights=self.weights)
        final_prices = self.paths[:, -1]  # Prix finaux des sous-jacents
        basket_price = np.dot(self.weights, final_prices)  # Moyenne pondérée
        expected_payoff = max(0, basket_price - self.strike)
        self.assertEqual(option.payoff(self.paths), expected_payoff)

    def test_basket_put_option(self):
        option = BasketPutOption(self.maturity, self.strike, weights=self.weights)
        final_prices = self.paths[:, -1]  # Prix finaux des sous-jacents
        basket_price = np.dot(self.weights, final_prices)  # Moyenne pondérée
        expected_payoff = max(0, self.strike - basket_price)
        self.assertEqual(option.payoff(self.paths), expected_payoff)

    def test_best_of_call_option(self):
        option = BestOfCallOption(self.maturity, self.strike)
        best_performance = np.max(self.paths[:, -1])  # Meilleur prix final parmi les sous-jacents
        expected_payoff = max(0, best_performance - self.strike)
        self.assertEqual(option.payoff(self.paths), expected_payoff)

    def test_best_of_put_option(self):
        option = BestOfPutOption(self.maturity, self.strike)
        best_performance = np.max(self.paths[:, -1])  # Meilleur prix final parmi les sous-jacents
        expected_payoff = max(0, self.strike - best_performance)
        self.assertEqual(option.payoff(self.paths), expected_payoff)

    def test_worst_of_call_option(self):
        option = WorstOfCallOption(self.maturity, self.strike)
        worst_performance = np.min(self.paths[:, -1])  # Pire prix final parmi les sous-jacents
        expected_payoff = max(0, worst_performance - self.strike)
        self.assertEqual(option.payoff(self.paths), expected_payoff)

    def test_worst_of_put_option(self):
        option = WorstOfPutOption(self.maturity, self.strike)
        worst_performance = np.min(self.paths[:, -1])  # Pire prix final parmi les sous-jacents
        expected_payoff = max(0, self.strike - worst_performance)
        self.assertEqual(option.payoff(self.paths), expected_payoff)

class TestOptionStrategies(unittest.TestCase):
    def setUp(self):
        # Initialisation des paramètres communs
        self.maturity = 1.0
        self.strike = 100
        self.strike_low = 90
        self.strike_high = 110
        self.strike_mid1 = 95
        self.strike_mid2 = 105
        self.maturity_near = 0.5
        self.maturity_far = 1.5
        self.path = np.array([90, 95, 100, 105])  # Exemple de chemin

    def test_straddle(self):
        strategy = Straddle(self.maturity, self.strike, position_call=True, position_put=True)
        call_payoff = max(0, self.path[-1] - self.strike)  # Long call
        put_payoff = max(0, self.strike - self.path[-1])  # Long put
        expected_payoff = call_payoff + put_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_strangle(self):
        strategy = Strangle(self.maturity, self.strike_high, self.strike_low, position_call=True, position_put=True)
        call_payoff = max(0, self.path[-1] - self.strike_high)  # Long call
        put_payoff = max(0, self.strike_low - self.path[-1])  # Long put
        expected_payoff = call_payoff + put_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_bull_spread(self):
        strategy = BullSpread(self.maturity, self.strike_low, self.strike_high, position_low=True, position_high=False)
        call_low_payoff = max(0, self.path[-1] - self.strike_low)  # Long call
        call_high_payoff = -max(0, self.path[-1] - self.strike_high)  # Short call
        expected_payoff = call_low_payoff + call_high_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_bear_spread(self):
        strategy = BearSpread(self.maturity, self.strike_low, self.strike_high, position_low=True, position_high=False)
        put_low_payoff = max(0, self.strike_low - self.path[-1])  # Long put
        put_high_payoff = -max(0, self.strike_high - self.path[-1])  # Short put
        expected_payoff = put_low_payoff + put_high_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_butterfly_spread(self):
        strategy = ButterflySpread(self.maturity, self.strike_low, self.strike_mid1, self.strike_high,
                                    position_low=True, position_mid=False, position_high=True)
        call_low_payoff = max(0, self.path[-1] - self.strike_low)  # Long call
        call_mid1_payoff = -max(0, self.path[-1] - self.strike_mid1)  # Short call
        call_mid2_payoff = -max(0, self.path[-1] - self.strike_mid1)  # Short call
        call_high_payoff = max(0, self.path[-1] - self.strike_high)  # Long call
        expected_payoff = call_low_payoff + call_mid1_payoff + call_mid2_payoff + call_high_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_condor_spread(self):
        strategy = CondorSpread(self.maturity, self.strike_low, self.strike_mid1, self.strike_mid2, self.strike_high,
                                 position_low=True, position_mid1=False, position_mid2=False, position_high=True)
        call_low_payoff = max(0, self.path[-1] - self.strike_low)  # Long call
        call_mid1_payoff = -max(0, self.path[-1] - self.strike_mid1)  # Short call
        call_mid2_payoff = -max(0, self.path[-1] - self.strike_mid2)  # Short call
        call_high_payoff = max(0, self.path[-1] - self.strike_high)  # Long call
        expected_payoff = call_low_payoff + call_mid1_payoff + call_mid2_payoff + call_high_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_calendar_spread(self):
        strategy = CalendarSpread(self.strike, self.maturity_near, self.maturity_far,
                                   position_near=False, position_far=True)
        call_near_payoff = -max(0, self.path[-1] - self.strike)  # Short call
        call_far_payoff = max(0, self.path[-1] - self.strike)  # Long call
        expected_payoff = call_near_payoff + call_far_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

    def test_collar(self):
        strategy = Collar(self.maturity, self.strike_high, self.strike_low,
                          position_call=False, position_put=True)
        call_payoff = -max(0, self.path[-1] - self.strike_high)  # Short call
        put_payoff = max(0, self.strike_low - self.path[-1])  # Long put
        expected_payoff = call_payoff + put_payoff
        self.assertEqual(strategy.payoff(self.path), expected_payoff)

if __name__ == "__main__":
    unittest.main()