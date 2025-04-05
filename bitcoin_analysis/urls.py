from django.urls import path
from . import views
from .dependency_injection import get_market_data_service

view_instance = views.AdvancedTechnicalAnalysis()
view_instance.market_data_service = get_market_data_service()


urlpatterns = [
    path('btc-indicators/', views.BitcoinTechnicalAnalysisAPI.as_view(), name='bta'),
    path('btc-analysis/', view_instance.as_view(), name='ata'),

]
