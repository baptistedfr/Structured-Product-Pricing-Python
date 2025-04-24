import json
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
from kernel.products import *
from kernel.tools import CalendarConvention, ObservationFrequency, Model
from kernel.market_data import InterpolationType, VolatilitySurfaceType, Market, RateCurveType
from kernel.models import MCPricingEngine, PricingEngineType
from kernel.pricing_launcher import PricingLauncher
from utils.pricing_settings import PricingSettings
from .utilities import *
from utils.day_counter import DayCounter
from kernel.products.rate.bond import *
from kernel.products.rate.vanilla_swap import InterestRateSwap
from datetime import datetime
# Lecture des tickers partagée pour éviter les répétitions
def get_tickers():
    """
    Cette fonction charge une fois les tickers depuis le fichier 'underlying_data.xlsx'.
    Cela évite de répéter cette opération dans chaque vue, améliorant ainsi les performances.
    """
    df_tickers = pd.read_excel('data/underlying_data.xlsx').iloc[1:,:]
    return df_tickers['Ticker'].unique().tolist()

def get_year_fraction(calendar_convention, start_date = datetime.now(), end_date = datetime.now()):
    """
    Cette fonction calcule la fraction d'année entre deux dates selon la convention de calendrier spécifiée.
    """
    day_counter = DayCounter(calendar_convention.value)
    return day_counter.get_year_fraction(start_date, end_date)

def get_ticker_data():
    """
    Charge les données des tickers depuis un fichier Excel.
    """
    return pd.read_excel('data/underlying_data.xlsx')

def get_ticker_price(request):
    """
    Récupère le prix du ticker demandé.
    """
    ticker = request.GET.get('ticker')
    
    # Charge les données des tickers une seule fois
    df_tickers = get_ticker_data()
    
    # Vérification de l'existence du ticker et récupération du prix
    ticker_price = df_tickers.loc[df_tickers['Ticker'] == ticker, "Last Price"]
    
    if ticker_price.empty:
        return JsonResponse({'error': 'Ticker not found'}, status=404)
    
    # Retourne le prix du ticker
    return JsonResponse({'ticker_price': str(ticker_price.iloc[0])})

# Lecture des options partagées pour éviter les répétitions
def get_options():
    """
    Cette fonction centralise la gestion des types d'options disponibles.
    Elle retourne un dictionnaire contenant différents types d'options.
    """
    return {
        'vanilla_options': [
            {'value': 'EuropeanCallOption', 'label': 'Call'},
            {'value': 'EuropeanPutOption', 'label': 'Put'}
        ],
        'path_dependent_options': [
            # {'value': 'AmericanCallOption', 'label': 'American Call'},
            # {'value': 'AmericanPutOption', 'label': 'American Put'},
            # {'value': 'BermudeanCallOption', 'label': 'Bermudean Call'},
            # {'value': 'BermudeanPutOption', 'label': 'Bermudean Put'},
            {'value': 'AsianCallOption', 'label': 'Asian Call'},
            {'value': 'AsianPutOption', 'label': 'Asian Put'},
            {'value': 'LookbackCallOption', 'label': 'Lookback Call'},
            {'value': 'LookbackPutOption', 'label': 'Lookback Put'},
            {'value': 'FloatingStrikeCallOption', 'label': 'Floating Strike Call'},
            {'value': 'FloatingStrikePutOption', 'label': 'Floating Strike Put'}
        ],
        'barrier_options': [
            {'value': 'UpAndInCallOption', 'label': 'Up-and-In Call'},
            {'value': 'UpAndOutCallOption', 'label': 'Up-and-Out Call'},
            {'value': 'DownAndInCallOption', 'label': 'Down-and-In Call'},
            {'value': 'DownAndOutCallOption', 'label': 'Down-and-Out Call'},
            {'value': 'UpAndInPutOption', 'label': 'Up-and-In Put'},
            {'value': 'DownAndInPutOption', 'label': 'Down-and-In Put'},
            {'value': 'UpAndOutPutOption', 'label': 'Up-and-Out Put'},
            {'value': 'DownAndOutPutOption', 'label': 'Down-and-Out Put'}
        ],
        'binary_options': [
            {'value': 'BinaryCallOption', 'label': 'Binary Call'},
            {'value': 'BinaryPutOption', 'label': 'Binary Put'}
        ]
    }

# Page d'accueil
def home_page(request):
    """
    Cette vue sert à afficher la page d'accueil.
    Elle ne contient que le rendu du template 'home.html'.
    """
    return render(request, 'home.html')

# Page "À propos"
def about_page(request):
    """
    Cette vue sert à afficher la page "À propos".
    Elle ne contient que le rendu du template 'about.html'.
    """
    return render(request, 'about.html')

# Pricer view, utilise get_tickers pour récupérer les tickers de manière optimisée
def pricer_view(request):
    """
    Cette vue sert à afficher la page des options à prix.
    Elle utilise get_tickers et get_options pour récupérer les données nécessaires.
    """
    options_data = get_options()  # Récupération des options
    context = {
        'tickers': get_tickers(),  # Utilisation de la fonction get_tickers
        'vol_types': [
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'ssvi', 'label': 'SSVI'},
            {'value': 'local', 'label': 'LocalVolatility'},
             {'value': 'heston', 'label': 'Heston'},
        ],
        'vanilla_options': json.dumps(options_data['vanilla_options']),
        'path_dependent_options': json.dumps(options_data['path_dependent_options']),
        'barrier_options': json.dumps(options_data['barrier_options']),
        'binary_options': json.dumps(options_data['binary_options']),
        'observation_frequencies': [
            {'value': 'annual', 'label': 'Annuelles'},
            {'value': 'semiannual', 'label': 'Semestrielles'},
            {'value': 'quarterly', 'label': 'Trimestrielles'},
            {'value': 'monthly', 'label': 'Mensuelles'}
        ]
    }
    return render(request, 'options.html', context)

# Fonction pour récupérer plusieurs strikes dans les paramètres GET
def get_strikes(request):
    """
    Cette fonction récupère tous les strikes passés en paramètres GET dans la requête.
    Elle renvoie une liste de strikes.
    """
    strikes = []
    i = 0
    while f"strike{i}" in request.GET:
        strikes.append(float(request.GET.get(f"strike{i}")))
        i += 1
    return strikes

# Calculer le prix d'une option
def calculate_price_options(request):
    """
    Cette vue sert à calculer le prix d'une option en fonction des paramètres reçus dans la requête GET.
    Elle utilise les paramètres de l'option pour calculer son prix et ses payoffs.
    """
    calendar_convention = CalendarConvention.ACT_360

    maturity_date = request.GET.get('maturity')
    maturity = get_year_fraction(calendar_convention, 
                                 datetime.now(), 
                                 datetime.strptime(maturity_date, '%Y-%m-%d'))
    
    
    # Validation du type d'option
    subtype = request.GET.get('subtype')
    if subtype not in OPTION_CLASSES:
        return JsonResponse({'error': 'Option type not recognized'}, status=400)

    pricing_engine_type = PricingEngineType.MC
    if subtype in american_like_options:
        pricing_engine_type = PricingEngineType.AMERICAN_MC
    
    bermudean_types = {'BermudeanCallOption', 'BermudeanPutOption'}
    exercise_times = None
    if subtype in bermudean_types:
        next_obs_date = request.GET.get('next_obs_date')
        obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
        next_exercise_time = get_year_fraction(calendar_convention, 
                                 datetime.now(), 
                                 datetime.strptime(next_obs_date, '%Y-%m-%d'))
        maturity = maturity
        obs_frequency = 1 / obs_frequency.value

        exercise_times = []
        while next_exercise_time < maturity:
            exercise_times.append(round(next_exercise_time, 6))  # arrondi pour éviter des erreurs flottantes
            next_exercise_time += obs_frequency
    

    # Créer l'option avec les paramètres
    option = create_option(
        option_type=subtype,
        maturity=maturity,
        strike=float(request.GET.get('strike', 100)),
        barrier=float(request.GET.get('barrier', None)) if request.GET.get('barrier') else None,
        coupon=float(request.GET.get('coupon', None)) if request.GET.get('coupon') else None,
        exercise_times=exercise_times
    )
    vol_type = request.GET.get('vol_type')
    if vol_type == 'heston':
        model = Model.HESTON
        volatility_surface_type = VolatilitySurfaceType.SVI
    else:
        model = Model.BLACK_SCHOLES
        volatility_surface_type = VOL_CONV.get(vol_type)

    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": None,
        "day_count_convention": calendar_convention,
        "model": model,
        "pricing_engine_type": pricing_engine_type,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": 1000,
        "random_seed": 4012,
        "compute_greeks": False,
    }

    settings = PricingSettings(**settings_dict)
    launcher = PricingLauncher(pricing_settings=settings)
    results = launcher.get_results(option)

    price = results.price
    try:
        greeks = results.greeks
    except : 
        greeks = {
            'delta': None,
            'gamma': None,
            'vega': None,
            'theta': None,
            'rho': None
        }

    # Générer le graphique de payoff
    prices = np.linspace(0.5 * float(request.GET.get('strike', 100)), 1.5 * float(request.GET.get('strike', 100)), 100)
    if subtype in american_like_options:
        payoffs = [option.instrinsec_payoff(p) for p in prices]
    else:
        payoffs = [option.payoff([p]) for p in prices]

    return JsonResponse({
        'price': round(price, 2),
        'greeks': greeks,
        'payoff_data': {
            'prices': prices.tolist(),
            'payoffs': payoffs
        }
    })

# Fonction pour les stratégies, utilise get_tickers pour récupérer les tickers
def strategies_view(request):
    """
    Cette vue sert à afficher la page des stratégies d'options.
    Elle utilise get_tickers pour récupérer les tickers.
    """
    context = {
        'tickers': get_tickers(),  # Utilisation de la fonction get_tickers
        'vol_types': [
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'ssvi', 'label': 'SSVI'},
            {'value': 'local', 'label': 'LocalVolatility'},
            {'value': 'heston', 'label': 'Heston'},
        ],
    }
    return render(request, 'options_strategies.html', context)

# Calculer le prix d'une stratégie
def calculate_price_strategy(request):
    """
    Cette vue sert à calculer le prix d'une stratégie d'options en fonction des paramètres reçus dans la requête GET.
    """
    strikes = get_strikes(request)  # Utilisation de la fonction get_strikes

    calendar_convention = CalendarConvention.ACT_360

    maturity_date = request.GET.get('maturity')
    maturity = get_year_fraction(calendar_convention, 
                                 datetime.now(), 
                                 datetime.strptime(maturity_date, '%Y-%m-%d'))
    
    # Créer la stratégie
    strategy = create_strategy(
        strategy_type=request.GET.get('strategy_type'),
        maturity=maturity,
        strikes=strikes,
        maturity_calendar=float(request.GET.get('maturity_calendar', None))  # Maturité pour CalendarSpread (optionnel)
    )

    vol_type = request.GET.get('vol_type')
    if vol_type == 'heston':
        model = Model.HESTON
        volatility_surface_type = VolatilitySurfaceType.SVI
    else:
        model = Model.BLACK_SCHOLES
        volatility_surface_type = VOL_CONV.get(vol_type)

    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": None,
        "day_count_convention": calendar_convention,
        "model": model,
        "pricing_engine_type": PricingEngineType.MC,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": 1000,
        "random_seed": 4012,
        "compute_greeks": False,
    }

    settings = PricingSettings(**settings_dict)
    launcher = PricingLauncher(settings)
    results = launcher.get_results(strategy)

    price = results.price
    greeks = results.greeks

    prices = np.linspace(0.5 * min(strikes), 1.5 * max(strikes), 100)
    payoffs = [strategy.payoff([p]) for p in prices]

    return JsonResponse({
        'price': round(price, 2),
        'greeks': greeks,
        'payoff_data': {
            'prices': prices.tolist(),
            'payoffs': payoffs
        }
    })

# Calculer le prix d'un autocall
def autocall_pricing_view(request):
    """
    Cette vue sert à afficher la page de pricing des autocalls.
    Elle utilise get_tickers pour récupérer les tickers.
    """
    context = {
        'tickers': get_tickers(),  # Utilisation de la fonction get_tickers
        'vol_types': [
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'ssvi', 'label': 'SSVI'},
            {'value': 'local', 'label': 'LocalVolatility'},
            {'value': 'heston', 'label': 'Heston'},
        ],
        'observation_frequencies': [
            {'value': 'annual', 'label': 'Annuelles'},
            {'value': 'semiannual', 'label': 'Semestrielles'},
            {'value': 'quarterly', 'label': 'Trimestrielles'},
            {'value': 'monthly', 'label': 'Mensuelles'}
        ]
    }
    return render(request, 'autocall_pricing.html', context)

# Calculer le coupon d'un autocall
def calculate_autocall_coupon(request):
    """
    Cette vue sert à calculer le coupon d'un autocall en fonction des paramètres reçus dans la requête GET.
    """
    obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
    
    calendar_convention = CalendarConvention.ACT_360

    maturity_date = request.GET.get('maturity')
    maturity = get_year_fraction(calendar_convention, 
                                 datetime.now(), 
                                 datetime.strptime(maturity_date, '%Y-%m-%d'))
    
    autocall = create_autocall(
        autocall_type=request.GET.get('autocall_type'),
        maturity=maturity,
        obs_frequency=obs_frequency,
        barriere_capital=float(request.GET.get('barriereCapital', None)),
        barriere_rappel=float(request.GET.get('barriereRappel', None)),
        barriere_coupon=float(request.GET.get('barriereCoupon', None)) if request.GET.get('barriereCoupon') else None,
        is_plus=request.GET.get('plusCheckbox', False) == 'on',
        is_security=request.GET.get('securityCheckbox', False) == 'on'
    )

    vol_type = request.GET.get('vol_type')
    if vol_type == 'heston':
        model = Model.HESTON
        volatility_surface_type = VolatilitySurfaceType.SVI
    else:
        model = Model.BLACK_SCHOLES
        volatility_surface_type = VOL_CONV.get(vol_type)

    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": obs_frequency,
        "day_count_convention": calendar_convention,
        "model": model,
        "pricing_engine_type": PricingEngineType.CALLABLE_MC,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": 1000,
        "random_seed": 4012,
        "compute_greeks": False,
    }

    settings = PricingSettings(**settings_dict)
    launcher_autocall = PricingLauncher(pricing_settings=settings)

    settings.compute_callable_coupons = True
    results_autocall = launcher_autocall.get_results(autocall)

    coupon = results_autocall.coupon_callable

    settings.compute_callable_coupons = False
    autocall.coupon_rate = coupon  # Mettre à jour le taux de coupon de l'autocall
    results_autocall = launcher_autocall.get_results(autocall)
    greeks = results_autocall.greeks

    return JsonResponse({
        'coupon': round(coupon, 2),
        'greeks': greeks,
    })

# Calculer le prix d'un autocall
def calculate_autocall_price(request):
    """
    Cette vue sert à calculer le coupon d'un autocall en fonction des paramètres reçus dans la requête GET.
    """
    obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
    
    calendar_convention = CalendarConvention.ACT_360

    maturity_date = request.GET.get('maturity')
    maturity = get_year_fraction(calendar_convention, 
                                 datetime.now(), 
                                 datetime.strptime(maturity_date, '%Y-%m-%d'))
    
    autocall = create_autocall(
        autocall_type=request.GET.get('autocall_type'),
        maturity=maturity,
        obs_frequency=obs_frequency,
        barriere_capital=float(request.GET.get('barriereCapital', None)),
        barriere_rappel=float(request.GET.get('barriereRappel', None)),
        barriere_coupon=float(request.GET.get('barriereCoupon', None)) if request.GET.get('barriereCoupon') else None,
        is_plus=request.GET.get('plusCheckbox', False) == 'on',
        is_security=request.GET.get('securityCheckbox', False) == 'on',
        coupon_rate = float(request.GET.get('coupon', 5.0)) if request.GET.get('coupon') else None
    )
    vol_type = request.GET.get('vol_type')
    if vol_type == 'heston':
        model = Model.HESTON
        volatility_surface_type = VolatilitySurfaceType.SVI
    else:
        model = Model.BLACK_SCHOLES
        volatility_surface_type = VOL_CONV.get(vol_type)

    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": obs_frequency,
        "day_count_convention": calendar_convention,
        "model": model,
        "pricing_engine_type": PricingEngineType.CALLABLE_MC,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": 1000,
        "random_seed": 4012,
        "compute_greeks": False,
    }

    settings = PricingSettings(**settings_dict)
    launcher_autocall = PricingLauncher(pricing_settings=settings)

    results_autocall = launcher_autocall.get_results(autocall)

    price = results_autocall.price
    greeks = results_autocall.greeks

    return JsonResponse({
        'price': round(price, 2),
        'greeks': greeks,
    })

# Page de produits de participation
def participation_products_view(request):
    """
    Cette vue sert à afficher la page de produits de participation.
    Elle utilise get_tickers pour récupérer les tickers.
    """
    context = {
        'tickers': get_tickers(),  # Utilisation de la fonction get_tickers
        'vol_types': [
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'ssvi', 'label': 'SSVI'},
            {'value': 'local', 'label': 'LocalVolatility'},
            {'value': 'heston', 'label': 'Heston'},
        ],
    }
    return render(request, 'participation_products.html', context)

# Calculer le prix d'un produit de participation (exemple statique ici)
def calculate_participation_products(request):
    """
    Cette vue sert à calculer un prix fictif pour les produits de participation.
    Elle renvoie une réponse JSON avec un prix fictif.
    """

    calendar_convention = CalendarConvention.ACT_360

    maturity_date = request.GET.get('maturity')
    maturity = get_year_fraction(calendar_convention, 
                                 datetime.now(), 
                                 datetime.strptime(maturity_date, '%Y-%m-%d'))
    
    # Créer la stratégie
    strategy = create_participation_product(
        product_type=request.GET.get('product_type'),
        maturity = maturity,
        upper_barrier=float(request.GET.get('barriereHaute', None)),
        lower_barrier=float(request.GET.get('barriereBasse', None)),
        rebate = float(request.GET.get('rebate', None)),
        leverage=float(request.GET.get('leverage', None))/100,
    )

    vol_type = request.GET.get('vol_type')
    if vol_type == 'heston':
        model = Model.HESTON
        volatility_surface_type = VolatilitySurfaceType.SVI
    else:
        model = Model.BLACK_SCHOLES
        volatility_surface_type = VOL_CONV.get(vol_type)

    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": None,
        "day_count_convention": calendar_convention,
        "model": model,
        "pricing_engine_type": PricingEngineType.MC,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": 1000,
        "random_seed": 4012,
        "compute_greeks": False,
    }

    settings = PricingSettings(**settings_dict)
    launcher = PricingLauncher(settings)
    results = launcher.get_results(strategy)

    price = results.price
    greeks = results.greeks

    initial_price = float(request.GET.get('ticker-price', 100))

    prices = np.linspace(0, 3 * initial_price, 100)
    payoffs = [strategy.payoff([initial_price, p]) for p in prices]

    return JsonResponse({
        'price': round(price, 2),
        'greeks': greeks,
        'payoff_data': {
            'prices': prices.tolist(),
            'payoffs': payoffs
        }
    })


# Calculer le prix d'un bond
def bond_pricing_view(request):
    """
    Cette vue sert à afficher la page de pricing des bonds.
    """
    context = {
        'calendar_conventions': [
            {'value': 'act_360', 'label': 'Actual/360'},
            {'value': 'act_365', 'label': 'Actual/365'},
            {'value': 'act_act', 'label': 'Actual/Actual'},
            {'value': '30_360', 'label': '30/360'}
        ],
        'observation_frequencies': [
            {'value': 'annual', 'label': 'Annuelles'},
            {'value': 'semiannual', 'label': 'Semestrielles'},
            {'value': 'quarterly', 'label': 'Trimestrielles'},
            {'value': 'monthly', 'label': 'Mensuelles'}
        ]
    }
    return render(request, 'bond_pricing.html', context)

# Calculer le coupon d'un bond
def calculate_bond_coupon(request):
    """
    Cette vue sert à calculer le coupon d'un autocall en fonction des paramètres reçus dans la requête GET.
    """
    obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
    calendar_convention = CALENDAR_CONVENTION.get(request.GET.get('calendar_convention'))


    maturity_date = datetime.strptime(request.GET.get('maturity'), "%Y-%m-%d")
    emission_date = datetime.strptime(request.GET.get('emission'), "%Y-%m-%d")
    value_date = datetime.strptime(request.GET.get('achat'), "%Y-%m-%d")

    notional = float(request.GET.get('notionel', 100))
    coupon_rate = float(request.GET.get('coupon', 5.0))/100 if request.GET.get('coupon') else None
    price = float(request.GET.get('price', 100)) if request.GET.get('price') else None
    bond = CouponBond(
        notional=notional,
        emission=emission_date,
        maturity=maturity_date,
        coupon_rate=coupon_rate,
        frequency=obs_frequency,
        calendar_convention=calendar_convention,
        price=price
    )
    settings_dict = {
        "underlying_name": "SPX",
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": VolatilitySurfaceType.SVI,
        "obs_frequency": obs_frequency,
        "day_count_convention": calendar_convention,
        "pricing_engine_type": PricingEngineType.RATE,
        "nb_paths": 100,
        "nb_steps": 1000,
        "random_seed": 4012,
    }
    settings = PricingSettings(**settings_dict)
    settings.valuation_date = value_date
    launcher_bond = PricingLauncher(settings)
    results_bond = launcher_bond.get_results(bond)
    ytm = results_bond.rate * 100
    return JsonResponse({
        'ytm': round(ytm, 4),
    })

# Calculer le prix d'un bond
def calculate_bond_price(request):
    """
    Cette vue sert à calculer le coupon d'un bond en fonction des paramètres reçus dans la requête GET.
    """
    obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
    calendar_convention = CALENDAR_CONVENTION.get(request.GET.get('calendar_convention'))


    maturity_date = datetime.strptime(request.GET.get('maturity'), "%Y-%m-%d")
    emission_date = datetime.strptime(request.GET.get('emission'), "%Y-%m-%d")
    value_date = datetime.strptime(request.GET.get('achat'), "%Y-%m-%d")

    notional = float(request.GET.get('notionel', 100))
    coupon_rate = float(request.GET.get('coupon', 5.0))/100 if request.GET.get('coupon') else None
    ytm = float(request.GET.get('ytm', 100))/100 if request.GET.get('ytm') else None
    bond = CouponBond(
        notional=notional,
        emission=emission_date,
        maturity=maturity_date,
        coupon_rate=coupon_rate,
        frequency=obs_frequency,
        calendar_convention=calendar_convention,
        ytm=ytm
    )
    settings_dict = {
        "underlying_name": "SPX",
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": VolatilitySurfaceType.SVI,
        "obs_frequency": obs_frequency,
        "day_count_convention": calendar_convention,
        "pricing_engine_type": PricingEngineType.RATE,
        "nb_paths": 100,
        "nb_steps": 1000,
        "random_seed": 4012,
    }
    settings = PricingSettings(**settings_dict)
    settings.valuation_date = value_date
    launcher_bond = PricingLauncher(settings)
    results_bond = launcher_bond.get_results(bond)
    price = results_bond.price
    return JsonResponse({
        'price': round(price, 2),
    })

# Calculer le prix d'un swap
def swap_pricing_view(request):
    """
    Cette vue sert à afficher la page de pricing des swaps.
    """
    context = {
        'calendar_conventions': [
            {'value': 'act_360', 'label': 'Actual/360'},
            {'value': 'act_365', 'label': 'Actual/365'},
            {'value': 'act_act', 'label': 'Actual/Actual'},
            {'value': '30_360', 'label': '30/360'}
        ],
        'observation_frequencies': [
            {'value': 'annual', 'label': 'Annuelles'},
            {'value': 'semiannual', 'label': 'Semestrielles'},
            {'value': 'quarterly', 'label': 'Trimestrielles'},
            {'value': 'monthly', 'label': 'Mensuelles'}
        ]
    }
    return render(request, 'swap_pricing.html', context)

# Calculer le rate d'un swap
def calculate_swap_rate(request):
    """
    Cette vue sert à calculer le rate d'un swap en fonction des paramètres reçus dans la requête GET.
    """
    obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
    calendar_convention = CALENDAR_CONVENTION.get(request.GET.get('calendar_convention'))


    maturity_date = datetime.strptime(request.GET.get('maturity'), "%Y-%m-%d")
    emission_date = datetime.strptime(request.GET.get('emission'), "%Y-%m-%d")
    value_date = datetime.strptime(request.GET.get('achat'), "%Y-%m-%d")

    notional = float(request.GET.get('notionel', 100))
   
    swap = InterestRateSwap(
        notional=notional,
        emission=emission_date,
        maturity=maturity_date,
        frequency=obs_frequency,
        calendar_convention=calendar_convention,
        price = 0
    )
    settings_dict = {
        "underlying_name": "SPX",
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": VolatilitySurfaceType.SVI,
        "obs_frequency": obs_frequency,
        "day_count_convention": calendar_convention,
        "pricing_engine_type": PricingEngineType.RATE,
        "nb_paths": 100,
        "nb_steps": 1000,
        "random_seed": 4012,
    }
    settings = PricingSettings(**settings_dict)
    settings.valuation_date = value_date
    launcher_swap = PricingLauncher(settings)
    swap_results = launcher_swap.get_results(swap)
    rate = swap_results.rate * 100
    return JsonResponse({
        'rate': round(rate, 2),
    })

# Calculer le prix d'un swap
def calculate_swap_price(request):
    """
    Cette vue sert à calculer le prix d'un swap en fonction des paramètres reçus dans la requête GET.
    """
    obs_frequency = OBS_FREQ.get(request.GET.get('obs_frequency'))
    calendar_convention = CALENDAR_CONVENTION.get(request.GET.get('calendar_convention'))

    maturity_date = datetime.strptime(request.GET.get('maturity'), "%Y-%m-%d")
    emission_date = datetime.strptime(request.GET.get('emission'), "%Y-%m-%d")
    value_date = datetime.strptime(request.GET.get('achat'), "%Y-%m-%d")

    notional = float(request.GET.get('notionel', 100))
    rate = float(request.GET.get('rate', 100))/100 if request.GET.get('rate') else None

    swap = InterestRateSwap(
        notional=notional,
        emission=emission_date,
        maturity=maturity_date,
        frequency=obs_frequency,
        calendar_convention=calendar_convention,
        fixed_rate=rate,
    )
    settings_dict = {
        "underlying_name": "SPX",
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": VolatilitySurfaceType.SVI,
        "obs_frequency": obs_frequency,
        "day_count_convention": calendar_convention,
        "pricing_engine_type": PricingEngineType.RATE,
        "nb_paths": 100,
        "nb_steps": 1000,
        "random_seed": 4012,
    }
    settings = PricingSettings(**settings_dict)
    settings.valuation_date = value_date
    launcher_swap = PricingLauncher(settings)
    swap_results = launcher_swap.get_results(swap)
    price = swap_results.price

    return JsonResponse({
        'price': round(price, 2),
    })