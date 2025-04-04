from kernel.products import *

OPTION_CLASSES = {
    'EuropeanCallOption': EuropeanCallOption,
    'EuropeanPutOption': EuropeanPutOption,
    'AsianCallOption': AsianCallOption,
    'AsianPutOption': AsianPutOption,
    'BinaryCallOption': BinaryCallOption,
    'BinaryPutOption': BinaryPutOption,
    'UpAndInCallOption': UpAndInCallOption,
    'UpAndOutCallOption': UpAndOutCallOption,
    'DownAndInCallOption': DownAndInCallOption,
    'DownAndOutCallOption': DownAndOutCallOption,
    'UpAndInPutOption': UpAndInPutOption,
    'DownAndInPutOption': DownAndInPutOption,
    'UpAndOutPutOption': UpAndOutPutOption,
    'DownAndOutPutOption': DownAndOutPutOption
}

def create_option(option_type, maturity, strike, barrier, coupon):
    # Crée l'option en fonction du type et des paramètres fournis
    if option_type in ['UpAndInCallOption', 'UpAndOutCallOption','DownAndInCallOption','DownAndOutCallOption',
                       'UpAndInPutOption', 'DownAndInPutOption', 'UpAndOutPutOption','DownAndOutPutOption']:  # Options barrières
        return OPTION_CLASSES[option_type](maturity=maturity, strike=strike, barrier=barrier)
    elif option_type in ['BinaryCallOption', 'BinaryPutOption']:  # Options binaires
        return OPTION_CLASSES[option_type](maturity=maturity, strike=strike, coupon=coupon)
    else:  # Options simples
        print(OPTION_CLASSES[option_type])
        return OPTION_CLASSES[option_type](maturity=maturity, strike=strike)
    

    # Pour les stratégies optionnelles

STRATEGY_CLASSES = {
    'Straddle': Straddle,
    'Strangle': Strangle,
    'BullSpread': BullSpread,
    'BearSpread': BearSpread,
    'ButterflySpread': ButterflySpread,
    'CondorSpread': CondorSpread,
    'CalendarSpread': CalendarSpread,
    'Collar': Collar,
}

def create_strategy(strategy_type, maturity, strike_call, strikes=None, maturity_calendar=None):
    """
    Crée une stratégie d'option basée sur le type et les paramètres fournis, où `strikes` est une liste.
    """

    if strategy_type == 'Straddle':
        # Straddle avec un seul strike pour le call et le put
        return Straddle(maturity, strike_call)
    
    elif strategy_type == 'Strangle':
        # Strangle avec deux strikes différents pour le call et le put
        if strikes is None or len(strikes) < 2:
            raise ValueError("Strangle nécessite deux strikes dans la liste: un pour le call et un pour le put")
        strike_put = strikes[1]  # Le deuxième strike est pour le put
        return Strangle(maturity, strike_call, strike_put)

    elif strategy_type == 'BullSpread':
        # BullSpread avec deux strikes : un bas (low) et un haut (high)
        if strikes is None or len(strikes) < 2:
            raise ValueError("BullSpread nécessite deux strikes dans la liste: un bas et un haut")
        strike_low, strike_high = strikes[0], strikes[1]
        return BullSpread(maturity, strike_low, strike_high)

    elif strategy_type == 'BearSpread':
        # BearSpread avec deux strikes : un haut (high) et un bas (low)
        if strikes is None or len(strikes) < 2:
            raise ValueError("BearSpread nécessite deux strikes dans la liste: un bas et un haut")
        strike_low, strike_high = strikes[0], strikes[1]
        return BearSpread(maturity, strike_low, strike_high)

    elif strategy_type == 'ButterflySpread':
        # ButterflySpread avec trois strikes : low, mid, high
        if strikes is None or len(strikes) < 3:
            raise ValueError("ButterflySpread nécessite trois strikes dans la liste: low, mid, high")
        strike_low, strike_mid, strike_high = strikes[0], strikes[1], strikes[2]
        return ButterflySpread(maturity, strike_low, strike_mid, strike_high)

    elif strategy_type == 'CondorSpread':
        # CondorSpread avec quatre strikes : low, mid1, mid2, high
        if strikes is None or len(strikes) < 4:
            raise ValueError("CondorSpread nécessite quatre strikes dans la liste: low, mid1, mid2, high")
        strike_low, strike_mid1, strike_mid2, strike_high = strikes[0], strikes[1], strikes[2], strikes[3]
        return CondorSpread(maturity, strike_low, strike_mid1, strike_mid2, strike_high)

    elif strategy_type == 'CalendarSpread':
        # CalendarSpread avec deux maturités et deux strikes : call et put
        if strike_call is None or strikes is None or len(strikes) < 1:
            raise ValueError("CalendarSpread nécessite des strikes 'call' et 'put' dans la liste")
        strike_put = strikes[0]  # Le premier strike dans la liste est pour le put
        if maturity_calendar is None:
            raise ValueError("CalendarSpread nécessite une seconde maturité (maturity_calendar)")
        return CalendarSpread(strike_call, maturity, maturity_calendar)

    elif strategy_type == 'Collar':
        # Collar avec un strike pour le call et un strike pour le put
        if strike_call is None or strikes is None or len(strikes) < 1:
            raise ValueError("Collar nécessite des strikes 'call' et 'put' dans la liste")
        strike_put = strikes[0]  # Le premier strike dans la liste est pour le put
        return Collar(maturity, strike_call, strike_put)

    else:
        raise ValueError(f"Type de stratégie '{strategy_type}' non reconnu.")