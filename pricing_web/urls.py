# pricing_web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),  # Page d'accueil
    path('about/', views.about_page, name='about'),  # Page À propos
    path('get_ticker_price', views.get_ticker_price, name='get_ticker_price'),
    path('options/', views.pricer_view, name='options_pricing'),
    path('options/strategies/', views.strategies_view, name='options_strategies_pricing'),
    path('calculate_price_options', views.calculate_price_options,  name='calculate_price_options')
]
