from django.urls import path
from . import views



urlpatterns = [
    path('btc-indicators/', views.BitcoinTechnicalAnalysisAPI.as_view(), name='bta'),
    path('btc-analysis/', views.AdvancedTechnicalAnalysis.as_view(), name='ata'),

]
