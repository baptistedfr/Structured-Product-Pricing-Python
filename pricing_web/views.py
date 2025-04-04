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
from kernel.tools import CalendarConvention
from kernel.market_data import InterpolationType, VolatilitySurfaceType, Market, RateCurveType
from kernel.models import MCPricingEngine, EulerSchemeType, PricingEngineType
from kernel.pricing_launcher import PricingLauncher
import json
from .utilities import create_option, OPTION_CLASSES


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
            {'value': 'AsianPutOption', 'label': 'Asian Put'}
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
            #{'value': 'heston', 'label': 'Heston'}
        ],
        'vanilla_options': json.dumps(options_data['vanilla_options']),
        'path_dependent_options': json.dumps(options_data['path_dependent_options']),
        'barrier_options': json.dumps(options_data['barrier_options']),
        'binary_options': json.dumps(options_data['binary_options'])
    }
    
    return render(request, 'options.html', context)


    
def calculate_price_options(request):
    # Récupération des paramètres de la requête
    ticker = request.GET.get('ticker')
    option_type = request.GET.get('option_type')
    subtype = request.GET.get('subtype')
    strike = float(request.GET.get('strike', 100))
    maturity = float(request.GET.get('maturity', 1))
    nb_steps = int(request.GET.get('nb_steps', 100))
    vol_type = request.GET.get('vol_type')
    constant_vol = float(request.GET.get('constant_vol', 0)) if request.GET.get('constant_vol') else None
    barrier = float(request.GET.get('barrier', None)) if request.GET.get('barrier') else None
    coupon = float(request.GET.get('coupon', None))  if request.GET.get('coupon') else None # Pour les options binaires (digitale)
    # Définition du type de volatilité
    if vol_type == "SVI":
        volatility_surface_type = VolatilitySurfaceType.SVI
    elif vol_type == "constant":
        volatility_surface_type = VolatilitySurfaceType.SVI
    else:
        volatility_surface_type = VolatilitySurfaceType.SVI

    # Création du marché avec les paramètres définis
    market = Market(
        underlying_name=ticker,
        rate_curve_type=RateCurveType.RF_US_TREASURY,
        interpolation_type=InterpolationType.SVENSSON,
        volatility_surface_type=volatility_surface_type,
        calendar_convention=CalendarConvention.ACT_360,
        obs_frequency=None
    )

    # Validation du type d'option
    if subtype not in OPTION_CLASSES:
        return JsonResponse({'error': 'Option type not recognized'}, status=400)

    # Création de l'option selon le type
    option = create_option(subtype, maturity, strike, barrier, coupon)

    # Création du lanceur de prix avec les paramètres du marché et de l'option
    pricer_type = PricingEngineType.MC  # Type de moteur de prix (Monte Carlo)
    launcher = PricingLauncher(
        market=market,
        discretization_method=EulerSchemeType.EULER,
        nb_paths=nb_steps,
        nb_steps=100,
        pricer_type=pricer_type
    )

    # Calcul du prix de l'option
    price = launcher.compute_price(option)
    print(price)

    greeks = launcher.pricer.compute_greeks(option).iloc[0].to_dict()
    # Génération du graphique de payoff
    prices = np.linspace(0.5 * strike, 1.5 * strike, 100)
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
    
    options_data = get_options()  # Récupération des options
    
    context = {
        'tickers': df_tickers['Ticker'].unique().tolist(),
        'vol_types': [
            {'value': 'constant', 'label': 'Volatilité Constante'},
            {'value': 'svi', 'label': 'SVI'},
            {'value': 'heston', 'label': 'Heston'}
        ],
        'vanilla_options': json.dumps(options_data['vanilla_options']),
        'path_dependent_options': json.dumps(options_data['path_dependent_options']),
        'barrier_options': json.dumps(options_data['barrier_options']),
        'binary_options': json.dumps(options_data['binary_options'])
    }
    
    return render(request, 'options_strategies.html', {})

def calculate_strategy_price(request):
    # Récupération des paramètres envoyés depuis le formulaire
    strategy_type = request.GET.get('strategy_type')
    maturity = float(request.GET.get('maturity'))
    strike = float(request.GET.get('strike'))
    price_put = float(request.GET.get('strike_put', strike))  # Valeur par défaut égale à strike
    strike_high = float(request.GET.get('strike_high', strike))  # Valeur par défaut égale à strike
    strike_mid = float(request.GET.get('strike_mid', strike))  # Valeur par défaut égale à strike
    strike_mid1 = float(request.GET.get('strike_mid1', strike))  # Valeur par défaut égale à strike
    strike_mid2 = float(request.GET.get('strike_mid2', strike))  # Valeur par défaut égale à strike
    maturity_far = float(request.GET.get('maturity_far', maturity))  # Valeur par défaut égale à maturity
    
    # Sélection de la stratégie en fonction de la donnée 'strategy_type'
    if strategy_type == 'straddle':
        strategy = Straddle(maturity, strike)
    elif strategy_type == 'strangle':
        strategy = Strangle(maturity, strike, price_put)
    elif strategy_type == 'bullspread':
        strategy = BullSpread(maturity, strike, strike_high)
    elif strategy_type == 'bearspread':
        strategy = BearSpread(maturity, strike, strike_high)
    elif strategy_type == 'butterflyspread':
        strategy = ButterflySpread(maturity, strike, strike_mid, strike_high)
    elif strategy_type == 'condorspread':
        strategy = CondorSpread(maturity, strike, strike_mid1, strike_mid2, strike_high)
    elif strategy_type == 'calendarspread':
        strategy = CalendarSpread(strike, maturity, maturity_far)
    elif strategy_type == 'collar':
        strategy = Collar(maturity, strike, price_put)
    else:
        return JsonResponse({'error': 'Stratégie inconnue'}, status=400)

    # Calcul du prix de l'option et des Grecs
    price = strategy.calculate_price()
    greeks = strategy.calculate_greeks()

    # Générer le graphique du payoff
    prices = np.linspace(0.5 * strike, 1.5 * strike, 100)
    payoffs = [strategy.payoff(p) for p in prices]
    
    

    # Retourner les résultats dans la réponse JSON
    return JsonResponse({
        'price': round(price, 2),
        'greeks': {
            'Delta': round(greeks['Delta'], 4),
            'Gamma': round(greeks['Gamma'], 4),
            'Vega': round(greeks['Vega'], 4),
            'Theta': round(greeks['Theta'], 4),
            'Rho': round(greeks['Rho'], 4),
        },
    })