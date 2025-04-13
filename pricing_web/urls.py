# pricing_web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),  # Page d'accueil
    path('about/', views.about_page, name='about'),  # Page À propos
    path('get_ticker_price', views.get_ticker_price, name='get_ticker_price'),

    path('options/', views.pricer_view, name='options_pricing'),
    path('options/strategies/', views.strategies_view, name='options_strategies_pricing'),

    path('calculate_price_options', views.calculate_price_options,  name='calculate_price_options'),
    path('calculate_price_strategy', views.calculate_price_strategy,  name='calculate_price_strategy'),

    path('autocalls/', views.autocall_pricing_view, name='autocall_pricing'),
    path('calculate_autocall_coupon', views.calculate_autocall_coupon,  name='calculate_autocall_coupon'),
    path('calculate_autocall_price', views.calculate_autocall_price,  name='calculate_autocall_price'),

    path('participation_products/', views.participation_products_view, name='participation_products_pricing'),
    path('calculate_participation_products', views.calculate_participation_products,  name='calculate_participation_products'),

    path('bond/', views.bond_pricing_view, name='bond_pricing'),
    path('calculate_bond_coupon', views.calculate_bond_coupon,  name='calculate_bond_coupon'),
    path('calculate_bond_price', views.calculate_bond_price,  name='calculate_bond_price'),

]
