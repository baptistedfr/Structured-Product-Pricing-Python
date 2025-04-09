import matplotlib
matplotlib.use('Agg')

from django.shortcuts import render
from django.http import JsonResponse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import base64

from kernel.products import *
from kernel.tools import CalendarConvention, ObservationFrequency, Model
from kernel.market_data import InterpolationType, VolatilitySurfaceType, Market, RateCurveType
from kernel.models import MCPricingEngine, EulerSchemeType, PricingEngineType
from kernel.pricing_launcher import PricingLauncher
from kernel.pricing_launcher_bis import PricingLauncherBis
from utils.pricing_settings import PricingSettings
import json
from kernel.models.pricing_engines.enum_pricing_engine import PricingEngineTypeBis
from .utilities import create_option, OPTION_CLASSES, create_strategy, VOL_CONV


def get_ticker_price(request):
    ticker = request.GET.get('ticker')
    df_tickers = pd.read_excel('data/underlying_data.xlsx')
    ticker_price = df_tickers.loc[df_tickers['Ticker'] == ticker, "Last Price"].iloc[0]
    return JsonResponse({'ticker_price': str(ticker_price)})

# Page d'accueil
def home_page(request):
    return render(request, 'home.html')

# Page "À propos"
def about_page(request):
    return render(request, 'about.html')

def get_options():
    return {
        'vanilla_options': [
            {'value': 'EuropeanCallOption', 'label': 'Call'},
            {'value': 'EuropeanPutOption', 'label': 'Put'}
        ],
        'path_dependent_options': [
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

def pricer_view(request):
    df_tickers = pd.read_excel('data/underlying_data.xlsx')
    
    options_data = get_options()  # Récupération des options
    
    context = {
        'tickers': df_tickers['Ticker'].unique().tolist(),
        'vol_types': [
            #{'value': 'constant', 'label': 'Volatilité Constante'},
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'ssvi', 'label': 'SSVI'},
            {'value': 'local', 'label': 'LocalVolatility'},
        ],
        'vanilla_options': json.dumps(options_data['vanilla_options']),
        'path_dependent_options': json.dumps(options_data['path_dependent_options']),
        'barrier_options': json.dumps(options_data['barrier_options']),
        'binary_options': json.dumps(options_data['binary_options'])
    }
    
    return render(request, 'options.html', context)


def calculate_price_options(request):
    # Récupération des paramètres de la requête

    constant_vol = float(request.GET.get('constant_vol', 0)) if request.GET.get('constant_vol') else None

    # Validation du type d'option
    if request.GET.get('subtype') not in OPTION_CLASSES:
        return JsonResponse({'error': 'Option type not recognized'}, status=400)
    # Définition du type de volatilité
    option, nb_steps = create_option(option_type = request.GET.get('subtype'), 
                                     maturity = float(request.GET.get('maturity', 1)), 
                                     strike = float(request.GET.get('strike', 100)), 
                                     barrier = float(request.GET.get('barrier', None)) if request.GET.get('barrier') else None, 
                                     coupon = float(request.GET.get('coupon', None))  if request.GET.get('coupon') else None)

    volatility_surface_type = VOL_CONV.get(request.GET.get('vol_type'))
    print(volatility_surface_type)
    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": None,
        "day_count_convention": CalendarConvention.ACT_360,
        "model": Model.BLACK_SCHOLES,
        "pricing_engine_type": PricingEngineTypeBis.MC_BIS,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": nb_steps,
        "random_seed": 4012,
        "compute_greeks": False,
    }
    settings = PricingSettings(**settings_dict)
    
    launcher_bis= PricingLauncherBis(pricing_settings=settings)
    results = launcher_bis.get_results(option)
   
    price = results.price
    print(price)

    greeks = results.greeks
    # Génération du graphique de payoff
    prices = np.linspace(0.5 * float(request.GET.get('strike', 100)), 1.5 * float(request.GET.get('strike', 100)), 100)
    payoffs = [option.payoff([p]) for p in prices]  # Calcul des payoffs

    # Retourner les résultats dans une réponse JSON
    return JsonResponse({
        'price': round(price, 2),
        'greeks': greeks,
        'payoff_data': {
        'prices': prices.tolist(),
        'payoffs': payoffs
        }
    })


def strategies_view(request):
    df_tickers = pd.read_excel('data/underlying_data.xlsx')
    
    context = {
        'tickers': df_tickers['Ticker'].unique().tolist(),
         'vol_types': [
            #{'value': 'constant', 'label': 'Volatilité Constante'},
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'ssvi', 'label': 'SSVI'},
            {'value': 'local', 'label': 'LocalVolatility'},
        ],
    }
    
    return render(request, 'options_strategies.html', context)

def calculate_price_strategy(request):

    strikes = []
    i = 0
    while f"strike{i}" in request.GET:
        strikes.append(float(request.GET.get(f"strike{i}")))
        i += 1

    # Crée la stratégie en fonction du type et des paramètres
    strategy = create_strategy(
            strategy_type = request.GET.get('strategy_type'), 
            maturity = float(request.GET.get('maturity', 1)), 
            strikes = strikes,
            maturity_calendar = float(request.GET.get('maturity_calendar', None))  # Maturité pour CalendarSpread (optionnel),
        )
    
    volatility_surface_type = VOL_CONV.get(request.GET.get('vol_type'))
    
    settings_dict = {
        "underlying_name": request.GET.get('ticker'),
        "rate_curve_type": RateCurveType.RF_US_TREASURY,
        "interpolation_type": InterpolationType.SVENSSON,
        "volatility_surface_type": volatility_surface_type,
        "obs_frequency": None,
        "day_count_convention": CalendarConvention.ACT_360,
        "model": Model.BLACK_SCHOLES,
        "pricing_engine_type": PricingEngineTypeBis.MC_BIS,
        "nb_paths": int(request.GET.get('nb_steps', 100)),
        "nb_steps": 1000,
        "random_seed": 4012,
        "compute_greeks": False,
    }
    settings = PricingSettings(**settings_dict)

    launcher = PricingLauncherBis(settings)

    results = launcher.get_results(strategy)
    

    
    price = results.price
    print(price)
    greeks = results.greeks
    prices = np.linspace(0.5 * min(strikes), 1.5 * max(strikes), 100)
    print(prices)
    payoffs = [strategy.payoff([p]) for p in prices]  # Calcul des payoffs
    print(payoffs)
    # Retourner les résultats dans une réponse JSON
    return JsonResponse({
        'price': round(price, 2),
        'greeks': greeks,
        'payoff_data': {
        'prices': prices.tolist(),
        'payoffs': payoffs
        }
    })
