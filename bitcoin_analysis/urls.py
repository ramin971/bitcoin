from django.urls import path
from . import views



urlpatterns = [
    path('btc-indicators/', views.bitcoin_indicators, name='btc'),

]
