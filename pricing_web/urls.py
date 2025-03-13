# pricing_web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),  # Page d'accueil
    path('about/', views.about_page, name='about'),  # Page À propos
]
