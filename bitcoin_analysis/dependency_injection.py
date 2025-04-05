from django.conf import settings
from market_data.fetchers import CoinGeckoFetcher #,BinanceFetcher
from market_data.service import MarketDataService

def get_market_data_service():
    """فکتوری برای ایجاد سرویس بر اساس تنظیمات"""
    if settings.MARKET_DATA_SOURCE == 'coingecko':
        return MarketDataService(CoinGeckoFetcher())
    # elif settings.MARKET_DATA_SOURCE == 'binance':
    #     return MarketDataService(BinanceFetcher())
    else:
        raise ValueError("Invalid market data source")