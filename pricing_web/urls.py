# pricing_web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),  # Page d'accueil
    path('about/', views.about_page, name='about'),  # Page À propos
    path('get_ticker_price', views.get_ticker_price, name='get_ticker_price'),
    path('options/vanilla/', views.pricer_view, name='vanilla_options_pricing'),
     path('get-price-options/', views.calculate_price_options, name='get_price_options')
]
