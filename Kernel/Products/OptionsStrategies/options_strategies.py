import numpy as np
from .abstract_option_strategy import AbstractOptionStrategy
from ..Options import *

class Straddle(AbstractOptionStrategy):
    """
    Représente une stratégie de straddle.
    """
    def __init__(self, maturity, strike, 
                 position_call=True, position_put=True):
        """
        Initialise une stratégie de straddle.

        :param maturity: Échéance des options.
        :param strike: Prix d'exercice commun pour le call et le put.
        :param position_call: Position sur le call (True pour long, False pour short).
        :param position_put: Position sur le put (True pour long, False pour short).
        """
        self.call = EuropeanCallOption(maturity, strike)
        self.put = EuropeanPutOption(maturity, strike)
        super().__init__([(self.call, position_call), (self.put, position_put)])

class Strangle(AbstractOptionStrategy):
    """
    Représente une stratégie de strangle.
    """
    def __init__(self, maturity, strike_call, strike_put, 
                 position_call=True, position_put=True):
        """
        Initialise une stratégie de strangle.

        :param maturity: Échéance des options.
        :param strike_call: Prix d'exercice pour le call.
        :param strike_put: Prix d'exercice pour le put.
        :param position_call: Position sur le call (True pour long, False pour short).
        :param position_put: Position sur le put (True pour long, False pour short).
        """
        self.call = EuropeanCallOption(maturity, strike_call)
        self.put = EuropeanPutOption(maturity, strike_put)
        super().__init__([(self.call, position_call), (self.put, position_put)])

class BullSpread(AbstractOptionStrategy):
    """
    Représente une stratégie de bull spread.
    """
    def __init__(self, maturity, strike_low, strike_high, 
                 position_low=True, position_high=False):
        """
        Initialise une stratégie de bull spread.

        :param maturity: Échéance des options.
        :param strike_low: Prix d'exercice de l'option achetée (long).
        :param strike_high: Prix d'exercice de l'option vendue (short).
        :param position_low: Position sur l'option avec strike_low (True pour long, False pour short).
        :param position_high: Position sur l'option avec strike_high (True pour long, False pour short).
        """
        self.call_low = EuropeanCallOption(maturity, strike_low)
        self.call_high = EuropeanCallOption(maturity, strike_high)
        super().__init__([(self.call_low, position_low), (self.call_high, position_high)])

class BearSpread(AbstractOptionStrategy):
    """
    Représente une stratégie de bear spread.
    """
    def __init__(self, maturity, strike_low, strike_high, 
                 position_low=True, position_high=False):
        """
        Initialise une stratégie de bear spread.

        :param maturity: Échéance des options.
        :param strike_low: Prix d'exercice de l'option achetée (long).
        :param strike_high: Prix d'exercice de l'option vendue (short).
        :param position_low: Position sur l'option avec strike_low (True pour long, False pour short).
        :param position_high: Position sur l'option avec strike_high (True pour long, False pour short).
        """
        self.put_low = EuropeanPutOption(maturity, strike_low)
        self.put_high = EuropeanPutOption(maturity, strike_high)
        super().__init__([(self.put_low, position_low), (self.put_high, position_high)])

class ButterflySpread(AbstractOptionStrategy):
    """
    Représente une stratégie de butterfly spread.
    """
    def __init__(self, maturity, strike_low, strike_mid, strike_high, 
                 position_low=True, position_mid=False, position_high=True):
        """
        Initialise une stratégie de butterfly spread.

        :param maturity: Échéance des options.
        :param strike_low: Prix d'exercice de l'option achetée (long).
        :param strike_mid: Prix d'exercice des options vendues (short).
        :param strike_high: Prix d'exercice de l'option achetée (long).
        :param position_low: Position sur l'option avec strike_low (True pour long, False pour short).
        :param position_mid: Position sur les options avec strike_mid (True pour long, False pour short).
        :param position_high: Position sur l'option avec strike_high (True pour long, False pour short).
        """
        self.call_low = EuropeanCallOption(maturity, strike_low)
        self.call_mid1 = EuropeanCallOption(maturity, strike_mid)
        self.call_mid2 = EuropeanCallOption(maturity, strike_mid)
        self.call_high = EuropeanCallOption(maturity, strike_high)
        super().__init__([
            (self.call_low, position_low),
            (self.call_mid1, position_mid),
            (self.call_mid2, position_mid),
            (self.call_high, position_high)
        ])

class CondorSpread(AbstractOptionStrategy):
    """
    Représente une stratégie de condor spread.
    """
    def __init__(self, maturity, strike_low, strike_mid1, strike_mid2, strike_high, 
                 position_low=True, position_mid1=False, position_mid2=False, position_high=True):
        """
        Initialise une stratégie de condor spread.

        :param maturity: Échéance des options.
        :param strike_low: Prix d'exercice de l'option achetée (long).
        :param strike_mid1: Prix d'exercice de la première option vendue (short).
        :param strike_mid2: Prix d'exercice de la deuxième option vendue (short).
        :param strike_high: Prix d'exercice de l'option achetée (long).
        :param position_low: Position sur l'option avec strike_low (True pour long, False pour short).
        :param position_mid1: Position sur l'option avec strike_mid1 (True pour long, False pour short).
        :param position_mid2: Position sur l'option avec strike_mid2 (True pour long, False pour short).
        :param position_high: Position sur l'option avec strike_high (True pour long, False pour short).
        """
        self.call_low = EuropeanCallOption(maturity, strike_low)
        self.call_mid1 = EuropeanCallOption(maturity, strike_mid1)
        self.call_mid2 = EuropeanCallOption(maturity, strike_mid2)
        self.call_high = EuropeanCallOption(maturity, strike_high)
        super().__init__([
            (self.call_low, position_low),
            (self.call_mid1, position_mid1),
            (self.call_mid2, position_mid2),
            (self.call_high, position_high)
        ])

class CalendarSpread(AbstractOptionStrategy):
    """
    Représente une stratégie de calendar spread.
    """
    def __init__(self, strike, maturity_near, maturity_far, 
                 position_near=False, position_far=True):
        """
        Initialise une stratégie de calendar spread.

        :param strike: Prix d'exercice commun pour les options.
        :param maturity_near: Échéance de l'option vendue (short).
        :param maturity_far: Échéance de l'option achetée (long).
        :param position_near: Position sur l'option avec échéance proche (True pour long, False pour short).
        :param position_far: Position sur l'option avec échéance lointaine (True pour long, False pour short).
        """
        self.call_near = EuropeanCallOption(maturity_near, strike)
        self.call_far = EuropeanCallOption(maturity_far, strike)
        super().__init__([(self.call_near, position_near), (self.call_far, position_far)])


class Collar(AbstractOptionStrategy):
    """
    Représente une stratégie de collar.
    """
    def __init__(self, maturity, strike_call, strike_put, 
                 position_call=False, position_put=True):
        """
        Initialise une stratégie de collar.

        :param maturity: Échéance des options.
        :param strike_call: Prix d'exercice de l'option call vendue (short).
        :param strike_put: Prix d'exercice de l'option put achetée (long).
        :param position_call: Position sur l'option call (True pour long, False pour short).
        :param position_put: Position sur l'option put (True pour long, False pour short).
        """
        self.call = EuropeanCallOption(maturity, strike_call)
        self.put = EuropeanPutOption(maturity, strike_put)
        super().__init__([(self.call, position_call), (self.put, position_put)])