from django.shortcuts import render
from django.http import JsonResponse
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import io
import base64
import json
import pandas as pd

from kernel.products import (EuropeanCallOption, EuropeanPutOption,
                               AsianCallOption, AsianPutOption, LookbackCallOption, LookbackPutOption,
                               UpAndInCallOption, UpAndOutCallOption, DownAndInCallOption, DownAndOutCallOption,
                               UpAndInPutOption, UpAndOutPutOption, DownAndInPutOption, DownAndOutPutOption,
                               BinaryCallOption, BinaryPutOption)

from kernel.tools import CalendarConvention
from kernel.market_data import InterpolationType, VolatilitySurfaceType, Market, RateCurveType
from kernel.models import MCPricingEngine, EulerSchemeType

def get_options():
    vanilla_options = [{'value': 'EuropeanCallOption', 'label': 'Call'}, 
                       {'value': 'EuropeanPutOption', 'label': 'Put'}]

    path_dependent_options = [{'value': 'AsianCallOption', 'label': 'Asian Call Option'}, 
                              {'value': 'AsianPutOption', 'label': 'Asian Put Option'}, 
                              {'value': 'LookbackCallOption', 'label': 'Lookback Call'},
                              {'value': 'LookbackPutOption', 'label': 'Lookback Put'}]

    barrier_options = [{'value': 'UpAndInCallOption', 'label': 'Up-and-In Call'}, 
                       {'value': 'UpAndOutCallOption', 'label': 'Up-and-Out Call'},
                       {'value': 'DownAndInCallOption', 'label': 'Down-and-In Call'},
                       {'value': 'DownAndOutCallOption', 'label': 'Down-and-Out Call'}]

    binary_options = [{'value': 'BinaryCallOption', 'label': 'Binary Call'}, 
                      {'value': 'BinaryPutOption', 'label': 'Binary Put'}]

    

    return {
        'vanilla_options': json.dumps(vanilla_options),
        'path_dependent_options': json.dumps(path_dependent_options),
        'barrier_options': json.dumps(barrier_options),
        'binary_options': json.dumps(binary_options),
    }
# Page d'accueil
def home_page(request):
    return render(request, 'home.html')

# Page "À propos"
def about_page(request):
    return render(request, 'about.html')

# Récupérer le prix d'un ticker
def get_ticker_price(request):
    ticker = request.GET.get('ticker')
    df_tickers = pd.read_excel('data/underlying_data.xlsx')
    ticker_price = df_tickers.loc[df_tickers['Ticker'] == ticker, "Last Price"].iloc[0]
    return JsonResponse({'ticker_price': str(ticker_price)})



def pricer_view(request):
    # Données pour les tickers
    df_tickers = pd.read_excel('data/underlying_data.xlsx')
    tickers = list(df_tickers['Ticker'].unique())
     # Types de volatilité
    vol_types = [{'value': 'constant', 'label': 'Volatilité Constante'}, 
                 {'value': 'svi', 'label': 'SVI'}, 
                 {'value': 'heston', 'label': 'Heston'}]
    # Récupérer les options configurées
    options = get_options()

    context = {
        'tickers': tickers,
        'vol_types': vol_types,
        **options,  # Injecter toutes les options dans le contexte
    }

    return render(request, 'vanilla_options.html', context)

# Calculer le prix des options
def calculate_price_options(request):
    print("here")
    try:
        # Récupérer les paramètres de la requête
        ticker = request.GET.get('ticker')
        option_type = request.GET.get('option_type')
        vol_type = request.GET.get('vol_type')
        strike = float(request.GET.get('strike', 100))
        maturity = float(request.GET.get('maturity', 1))
        nb_steps = int(request.GET.get('nb_steps', 100))
        barrier = request.GET.get('barrier')
        payout = request.GET.get('payout')
        coupon = request.GET.get('coupon')
        constant_vol = request.GET.get('constant_vol')

        # Initialiser le marché
        market = Market(
            underlying_name=ticker,
            rate_curve_type=RateCurveType.RF_US_TREASURY,
            interpolation_type=InterpolationType.SVENSSON,
            volatility_surface_type=VolatilitySurfaceType.SVI,
            calendar_convention=CalendarConvention.ACT_360
        )

        # Gestion de la volatilité
        if vol_type == 'constant' and constant_vol:
            volatility = float(constant_vol)
        elif vol_type == 'heston':
            volatility = 0.25
        elif vol_type == 'svi':
            volatility = 0.3
        else:
            volatility = 0.2

        # Créer l'option en fonction du type
        option = None
        if option_type == 'EuropeanCallOption':
            option = EuropeanCallOption(maturity=maturity, strike=strike)
        elif option_type == 'european_put':
            option = EuropeanPutOption(maturity=maturity, strike=strike)
        elif option_type == 'asian_call':
            option = AsianCallOption(maturity=maturity, strike=strike)
        elif option_type == 'asian_put':
            option = AsianPutOption(maturity=maturity, strike=strike)
        elif option_type == 'binary_call':
            option = BinaryCallOption(maturity=maturity, strike=strike, payout=float(payout or 0))
        elif option_type == 'binary_put':
            option = BinaryPutOption(maturity=maturity, strike=strike, payout=float(payout or 0))
        elif option_type == 'up_and_in_call':
            option = UpAndInCallOption(maturity=maturity, strike=strike, barrier=float(barrier or 0))
        elif option_type == 'down_and_out_put':
            option = DownAndOutPutOption(maturity=maturity, strike=strike, barrier=float(barrier or 0))
        else:
            return JsonResponse({'error': 'Invalid option type'}, status=400)

        # Initialiser le moteur de pricing
        engine = MCPricingEngine(
            market=market,
            discretization_method=EulerSchemeType.FULL_TRUNCATION,
            nb_paths=100000,
            nb_steps=nb_steps
        )

        # Calculer le prix
        price = engine.compute_price(option)

        # Générer le graphique du payoff
        prices = np.linspace(0.5 * strike, 1.5 * strike, 100)
        if isinstance(option, (EuropeanCallOption, AsianCallOption)):
            payoffs = np.maximum(prices - strike, 0)
        elif isinstance(option, (EuropeanPutOption, AsianPutOption)):
            payoffs = np.maximum(strike - prices, 0)
        elif isinstance(option, BinaryCallOption):
            payoffs = np.where(prices > strike, float(payout or 0), 0)
        elif isinstance(option, BinaryPutOption):
            payoffs = np.where(prices < strike, float(payout or 0), 0)
        elif isinstance(option, (UpAndInCallOption, DownAndOutPutOption)):
            payoffs = np.maximum(prices - strike, 0)  # Exemple simplifié
        else:
            payoffs = np.zeros_like(prices)

        plt.figure(figsize=(8, 5))
        plt.plot(prices, payoffs, label=f'{option_type.capitalize()} Payoff')
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.axvline(strike, color='red', linewidth=0.8, linestyle='--', label='Strike')
        plt.title('Payoff en fonction du prix spot')
        plt.xlabel('Prix Spot')
        plt.ylabel('Payoff')
        plt.legend()
        plt.grid()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        graph = base64.b64encode(image_png).decode('utf-8')

        return JsonResponse({'price': round(price, 2), 'volatility': volatility, 'payoff_graph': f'data:image/png;base64,{graph}'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
