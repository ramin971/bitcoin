import requests
import pandas as pd
from abc import ABC, abstractmethod
from django.core.cache import cache

class BaseMarketDataFetcher(ABC):
    """اینترفیس پایه برای دریافت داده‌های بازار"""
    
    @abstractmethod
    def fetch_data(self, symbol: str, days: int = 365, interval: str = 'daily') -> pd.DataFrame:
        pass

class CoinGeckoFetcher(BaseMarketDataFetcher):
    """پیاده‌سازی دریافت داده از CoinGecko API"""
    
    def __init__(self, cache_timeout: int = 3600):
        self.cache_timeout = cache_timeout
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def fetch_data(self, symbol: str, days: int = 365, interval: str = 'daily') -> pd.DataFrame:
        cache_key = f"market_data_{symbol}_{days}_{interval}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return pd.DataFrame(cached_data)
        
        try:
            url = f"{self.base_url}/coins/{symbol}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': interval
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            df = self._process_data(data)
            cache.set(cache_key, df.to_dict('records'), self.cache_timeout)
            return df
            
        except Exception as e:
            raise MarketDataFetchError(f"Error fetching data: {str(e)}")

    def _process_data(self, data: dict) -> pd.DataFrame:
        """پردازش داده‌های خام به DataFrame"""
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        
        if 'total_volumes' in data:
            volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
            volumes['date'] = pd.to_datetime(volumes['timestamp'], unit='ms')
            volumes.set_index('date', inplace=True)
            df['volume'] = volumes['volume']
        
        return df[~df.index.duplicated(keep='first')]

class MarketDataFetchError(Exception):
    """خطای سفارشی برای مشکلات دریافت داده"""
    pass