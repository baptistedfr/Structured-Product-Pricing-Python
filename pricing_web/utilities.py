from kernel.products import *
from kernel.market_data.volatility_surface.enums_volatility import VolatilitySurfaceType
from kernel.tools import  ObservationFrequency
VOL_CONV = {
    "svi" : VolatilitySurfaceType.SVI,
    "ssvi" : VolatilitySurfaceType.SSVI,
    "local" : VolatilitySurfaceType.LOCAL,
}

OBS_FREQ = {
    "annual" : ObservationFrequency.ANNUAL,
    "semiannual" : ObservationFrequency.SEMIANNUAL,
    "quarterly" : ObservationFrequency.QUARTERLY,
    "monthly" : ObservationFrequency.MONTHLY,
}

OPTION_CLASSES = {
    'EuropeanCallOption': EuropeanCallOption,
    'EuropeanPutOption': EuropeanPutOption,

    'AsianCallOption': AsianCallOption,
    'AsianPutOption': AsianPutOption,
    'FloatingStrikeCallOption': FloatingStrikeCallOption,
    'FloatingStrikePutOption': FloatingStrikePutOption,
    'LookbackCallOption': LookbackCallOption,
    'LookbackPutOption': LookbackPutOption,

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
        return OPTION_CLASSES[option_type](maturity=maturity, strike=strike)
    

    # Pour les stratégies optionnelles

STRATEGY_CLASSES = {
    'Straddle': Straddle,
    'Strangle': Strangle,
    'BullSpread': BullSpread,
    'BearSpread': BearSpread,
    'ButterflySpread': ButterflySpread,
    'CondorSpread': CondorSpread,
    'Strip' : Strip,
    'Strap' : Strap,
    'CalendarSpread': CalendarSpread,
    'Collar': Collar,
}

def create_strategy(strategy_type, maturity, strikes=None, maturity_calendar=None):
    """
    Crée une stratégie d'option basée sur le type et les paramètres fournis, où `strikes` est une liste.
    """

    if strategy_type == 'straddle':
        # Straddle avec un seul strike pour le call et le put
        return Straddle(maturity, strikes[0])
    
    elif strategy_type == 'strangle':
        # Strangle avec deux strikes différents pour le call et le put
        if strikes is None or len(strikes) < 2:
            raise ValueError("Strangle nécessite deux strikes dans la liste: un pour le call et un pour le put")
        return Strangle(maturity, strike_put = min(strikes), strike_call = max(strikes))

    elif strategy_type == 'bull_spread':
        # BullSpread avec deux strikes : un bas (low) et un haut (high)
        if strikes is None or len(strikes) < 2:
            raise ValueError("BullSpread nécessite deux strikes dans la liste: un bas et un haut")
        strike_low, strike_high = min(strikes), max(strikes)
        return BullSpread(maturity, strike_low, strike_high)

    elif strategy_type == 'bear_spread':
        # BearSpread avec deux strikes : un haut (high) et un bas (low)
        if strikes is None or len(strikes) < 2:
            raise ValueError("BearSpread nécessite deux strikes dans la liste: un bas et un haut")
        strike_low, strike_high = min(strikes), max(strikes)
        return BearSpread(maturity, strike_low, strike_high)

    elif strategy_type == 'butterfly_spread':
        # ButterflySpread avec trois strikes : low, mid, high
        if strikes is None or len(strikes) != 3:
            raise ValueError("ButterflySpread nécessite trois strikes dans la liste: low, mid, high")
        strikes.sort()
        strike_low, strike_mid, strike_high = strikes[0], strikes[1], strikes[2]
        return ButterflySpread(maturity, strike_low, strike_mid, strike_high)

    elif strategy_type == 'strip':
        if strikes is None or len(strikes) != 1:
            raise ValueError("Strip nécessite 1 strike")
        
        return Strip(maturity, strikes[0])

    elif strategy_type == 'strap':
        if strikes is None or len(strikes) != 1:
            raise ValueError("Strap nécessite 1 strike")
        
        return Strap(maturity, strikes[0])
    
    elif strategy_type == 'calendar_spread':
        # CalendarSpread avec deux maturités et deux strikes : call et put
        if strikes is None or len(strikes) < 1:
            raise ValueError("CalendarSpread nécessite des strikes 'call' et 'put' dans la liste")  # Le premier strike dans la liste est pour le put
        if maturity_calendar is None:
            raise ValueError("CalendarSpread nécessite une seconde maturité (maturity_calendar)")
        return CalendarSpread(strikes[0], maturity, maturity_calendar)

    # elif strategy_type == 'Collar':
    #     # Collar avec un strike pour le call et un strike pour le put
    #     if strikes is None or len(strikes) < 2:
    #         raise ValueError("Collar nécessite des strikes 'call' et 'put' dans la liste")
         
    #     return Collar(maturity, strikes[0], strikes[1])
    else:
        raise ValueError(f"Type de stratégie '{strategy_type}' non reconnu.")
    

def create_autocall(autocall_type, maturity, obs_frequency, barriere_capital, barriere_rappel, barriere_coupon, is_plus, is_security, coupon_rate = 5.0):
    print(coupon_rate)
    if autocall_type == 'phoenix':
        # Straddle avec un seul strike pour le call et le put
        return Phoenix(maturity=maturity, 
                       observation_frequency=obs_frequency, 
                       capital_barrier=barriere_capital, 
                       autocall_barrier=barriere_rappel, 
                       coupon_barrier=barriere_coupon, 
                       coupon_rate=coupon_rate,
                       is_security = is_security,
                       is_plus = is_plus)
    
    elif autocall_type == 'eagle':
       return Eagle(maturity=maturity, 
                       observation_frequency=obs_frequency, 
                       capital_barrier=barriere_capital, 
                       autocall_barrier=barriere_rappel, 
                       coupon_rate=coupon_rate,
                       is_security = is_security,
                       is_plus = is_plus)
    else:
        raise ValueError(f"Type d'autocall '{autocall_type}' non reconnu.")
    
def create_participation_product(product_type, maturity, upper_barrier, lower_barrier, leverage, rebate):
    print(leverage, rebate)
    if product_type == 'twinwin':

        return TwinWin(maturity=maturity, 
                       upper_barrier=upper_barrier, 
                       lower_barrier=lower_barrier, 
                       leverage=leverage, 
                       rebate=rebate)
    
    elif product_type == 'airbag':
        return Airbag(maturity=maturity, 
                       upper_barrier=upper_barrier, 
                       lower_barrier=lower_barrier, 
                       leverage=leverage, 
                       rebate=rebate)
    else:
        raise ValueError(f"Type d'autocall '{product_type}' non reconnu.")