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