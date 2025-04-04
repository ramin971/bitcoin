from django.urls import path
from . import views



urlpatterns = [
    path('btc-indicators/', views.BitcoinTechnicalAnalysisAPI.as_view(), name='btc'),

]
