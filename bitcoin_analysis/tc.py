import requests
import pandas as pd
from ta.trend import (
    MACD, EMAIndicator, SMAIndicator, 
    IchimokuIndicator,CCIIndicator,
    ADXIndicator, PSARIndicator
)
from ta.momentum import (
    RSIIndicator, StochasticOscillator,
    WilliamsRIndicator
)

from ta.volatility import BollingerBands , AverageTrueRange as ATR
from ta.volume import AccDistIndexIndicator, MFIIndicator, OnBalanceVolumeIndicator



def fetch_market_data():
    """دریافت داده‌های بازار از CoinGecko API"""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': 365,
        'interval': 'daily'
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    # ایجاد DataFrame
    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    
    # اضافه کردن حجم معاملات اگر موجود باشد
    if 'total_volumes' in data:
        volumes = pd.DataFrame(data['total_volumes'], 
                             columns=['timestamp', 'volume'])
        volumes['date'] = pd.to_datetime(volumes['timestamp'], unit='ms')
        volumes.set_index('date', inplace=True)
        df['volume'] = volumes['volume']
    
    # حذف داده‌های تکراری و مرتب‌سازی
    df = df[~df.index.duplicated(keep='first')]
    df.sort_index(inplace=True)
    
    return df





class TechnicalCalculator:
    """کلاس پایه برای محاسبات اندیکاتورها"""

        
    def calculate_all(self,df):
        """محاسبه تمام اندیکاتورها"""
        self.df = df.copy()
        self._calculate_trend_indicators()
        self._calculate_momentum_indicators()
        self._calculate_volume_indicators()
        self._calculate_volatility_indicators()
        return self.df
    
    def _calculate_trend_indicators(self):
        # محاسبه میانگین‌های متحرک
        self.df['sma20'] = SMAIndicator(close=self.df['price'], window=20).sma_indicator()
        self.df['sma50'] = SMAIndicator(close=self.df['price'], window=50).sma_indicator()
        self.df['sma200'] = SMAIndicator(close=self.df['price'], window=200).sma_indicator()
        self.df['ema12'] = EMAIndicator(close=self.df['price'], window=12).ema_indicator()
        self.df['ema26'] = EMAIndicator(close=self.df['price'], window=26).ema_indicator()
        
        # محاسبه MACD
        macd = MACD(close=self.df['price'], window_slow=26, window_fast=12, window_sign=9)
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        self.df['macd_hist'] = macd.macd_diff()
        
        # محاسبه ADX
        adx = ADXIndicator(
            high=self.df['price'], low=self.df['price'], 
            close=self.df['price'], window=14
        )
        self.df['adx'] = adx.adx()
        self.df['adx_pos'] = adx.adx_pos()
        self.df['adx_neg'] = adx.adx_neg()
        
        # محاسبه ایچیموکو
        ichimoku = IchimokuIndicator(
            high=self.df['price'], low=self.df['price'],
            window1=9, window2=26, window3=52
        )
        self.df['ichi_conv'] = ichimoku.ichimoku_conversion_line()
        self.df['ichi_base'] = ichimoku.ichimoku_base_line()
        self.df['ichi_a'] = ichimoku.ichimoku_a()
        self.df['ichi_b'] = ichimoku.ichimoku_b()

        #  محاسبه پارابولیک SAR
        self.df['psar'] = PSARIndicator(
            high=self.df['price'], low=self.df['price'], 
            close=self.df['price'], step=0.02, max_step=0.2
        ).psar()
        
        return self.df
    
    def _calculate_momentum_indicators(self):
        # محاسبه RSI
        self.df['rsi14'] = RSIIndicator(close=self.df['price'], window=14).rsi()
        
        # محاسبه استوکاستیک
        stoch = StochasticOscillator(
            high=self.df['price'], low=self.df['price'],
            close=self.df['price'], window=14, smooth_window=3
        )
        self.df['stoch_k'] = stoch.stoch()
        self.df['stoch_d'] = stoch.stoch_signal()
        
        # محاسبه CCI
        self.df['cci20'] = CCIIndicator(
            high=self.df['price'], low=self.df['price'],
            close=self.df['price'], window=20
        ).cci()

        #  محاسبه Williams %R
        self.df['williams14'] = WilliamsRIndicator(
            high=self.df['price'], low=self.df['price'], 
            close=self.df['price'], lbp=14
        ).williams_r()
        
        return self.df
    
    def _calculate_volume_indicators(self):
        if 'volume' in self.df.columns:
            # محاسبه MFI
            self.df['mfi14'] = MFIIndicator(
                high=self.df['price'], low=self.df['price'],
                close=self.df['price'], volume=self.df['volume'], window=14
            ).money_flow_index()
            
            # محاسبه OBV
            self.df['obv'] = OnBalanceVolumeIndicator(
                close=self.df['price'], volume=self.df['volume']
            ).on_balance_volume()

            # محاسبه Accumulation/Distribution
            self.df['adl'] = AccDistIndexIndicator(
                high=self.df['price'], low=self.df['price'], 
                close=self.df['price'], volume=self.df['volume']
            ).acc_dist_index()
        
        return self.df
    
    def _calculate_volatility_indicators(self):
        # محاسبه بولینگر باندز
        bb = BollingerBands(close=self.df['price'], window=20, window_dev=2)
        self.df['bb_upper'] = bb.bollinger_hband()
        self.df['bb_middle'] = bb.bollinger_mavg()
        self.df['bb_lower'] = bb.bollinger_lband()
        self.df['bb_width'] = (self.df['bb_upper'] - self.df['bb_lower']) / self.df['bb_middle']
        
        # محاسبه ATR
        self.df['atr14'] = ATR(
            high=self.df['price'], low=self.df['price'],
            close=self.df['price'], window=14
        ).average_true_range()
        



 


        


 


        

        

        

        

        
