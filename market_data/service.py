from .fetchers import CoinGeckoFetcher, BaseMarketDataFetcher
import pandas as pd

class MarketDataService:
    """سرویس مدیریت دریافت داده‌های بازار"""
    
    def __init__(self, fetcher: BaseMarketDataFetcher = None):
        self.fetcher = fetcher or CoinGeckoFetcher()
    
    def get_historical_data(self, symbol: str, **kwargs) -> pd.DataFrame:
        """دریافت داده‌های تاریخی"""
        return self.fetcher.fetch_data(symbol, **kwargs)