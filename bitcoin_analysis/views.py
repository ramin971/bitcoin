# from .indicators import calculate_indicators
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

# @api_view(['GET'])
# def bitcoin_indicators(request):
#     data = calculate_indicators()
#     return Response(data)

# import requests
# import pandas as pd
# # import numpy as np
# from ta.trend import (MACD, EMAIndicator, SMAIndicator, 
#                      BollingerBands, IchimokuIndicator, 
#                      ADXIndicator, ATR, PSARIndicator)
# from ta.momentum import (RSIIndicator, StochasticOscillator, 
#                         WilliamsRIndicator, MFIIndicator, 
#                         ROCIndicator, TSIIndicator)
# from ta.volume import AccDistIndexIndicator, ChaikinMoneyFlowIndicator
# from ta.others import CCIIndicator
# from django.http import JsonResponse
# from django.views import View
# from django.core.cache import cache




# class BitcoinTechnicalAnalysis(View):
#     def get(self, request):
#         # چک کردن کش
#         cached_data = cache.get('bitcoin_technical_analysis')
#         if cached_data:
#             return JsonResponse(cached_data)

#         # دریافت داده از CoinGecko
#         try:
#             df = self.fetch_bitcoin_data()
#             analysis = self.calculate_technical_analysis(df)
            
#             # ذخیره در کش به مدت 1 ساعت
#             cache.set('bitcoin_technical_analysis', analysis, 3600)
            
#             return JsonResponse(analysis)
            
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     def fetch_bitcoin_data(self):
#         """دریافت داده‌های تاریخی بیت‌کوین از CoinGecko"""
#         url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
#         params = {
#             'vs_currency': 'usd',
#             'days': '365',
#             'interval': 'daily'
#         }
        
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
        
#         # تبدیل به DataFrame
#         df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
#         df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
#         df.set_index('date', inplace=True)
#         df = df[~df.index.duplicated(keep='first')]
#         df.sort_index(inplace=True)
        
#         return df

#     def calculate_technical_analysis(self, df):
#         """محاسبه تحلیل تکنیکال"""
#         # محاسبه اندیکاتورها
#         df['sma50'] = SMAIndicator(close=df['price'], window=50).sma_indicator()
#         df['sma200'] = SMAIndicator(close=df['price'], window=200).sma_indicator()
#         df['ema12'] = EMAIndicator(close=df['price'], window=12).ema_indicator()
#         df['ema26'] = EMAIndicator(close=df['price'], window=26).ema_indicator()
        
#         # محاسبه MACD
#         macd = MACD(close=df['price'], window_slow=26, window_fast=12, window_sign=9)
#         df['macd'] = macd.macd()
#         df['macd_signal'] = macd.macd_signal()
        
#         # محاسبه RSI
#         df['rsi'] = RSIIndicator(close=df['price'], window=14).rsi()
        
#         # تعیین وضعیت هر اندیکاتور
#         analysis = {
#             'price': {
#                 'value': float(df['price'].iloc[-1]),
#                 'trend': 'up' if df['price'].iloc[-1] > df['price'].iloc[-2] else 'down'
#             },
#             'sma50': {
#                 'value': float(df['sma50'].iloc[-1]),
#                 'trend': 'up' if df['sma50'].iloc[-1] > df['sma50'].iloc[-2] else 'down',
#                 'position': 'above_price' if df['sma50'].iloc[-1] > df['price'].iloc[-1] else 'below_price'
#             },
#             'sma200': {
#                 'value': float(df['sma200'].iloc[-1]),
#                 'trend': 'up' if df['sma200'].iloc[-1] > df['sma200'].iloc[-2] else 'down',
#                 'position': 'above_price' if df['sma200'].iloc[-1] > df['price'].iloc[-1] else 'below_price'
#             },
#             'golden_cross': {
#                 'value': 'active' if df['sma50'].iloc[-1] > df['sma200'].iloc[-1] and 
#                                  df['sma50'].iloc[-2] <= df['sma200'].iloc[-2] else 'inactive',
#                 'status': 'bullish' if df['sma50'].iloc[-1] > df['sma200'].iloc[-1] else 'bearish'
#             },
#             'macd': {
#                 'value': float(df['macd'].iloc[-1]),
#                 'signal': float(df['macd_signal'].iloc[-1]),
#                 'trend': 'bullish' if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] else 'bearish',
#                 'momentum': 'increasing' if df['macd'].iloc[-1] > df['macd'].iloc[-2] else 'decreasing'
#             },
#             'rsi': {
#                 'value': float(df['rsi'].iloc[-1]),
#                 'trend': 'up' if df['rsi'].iloc[-1] > df['rsi'].iloc[-2] else 'down',
#                 'status': 'overbought' if df['rsi'].iloc[-1] > 70 else 
#                          'oversold' if df['rsi'].iloc[-1] < 30 else 'neutral'
#             },
#             'ema_cross': {
#                 'value': 'active' if df['ema12'].iloc[-1] > df['ema26'].iloc[-1] and 
#                                  df['ema12'].iloc[-2] <= df['ema26'].iloc[-2] else 'inactive',
#                 'status': 'bullish' if df['ema12'].iloc[-1] > df['ema26'].iloc[-1] else 'bearish'
#             },
#             'last_updated': pd.Timestamp.now().isoformat()
#         }
        
#         return analysis

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
from ta.volume import AccDistIndexIndicator, MFIIndicator
# from django.http import JsonResponse
# from django.views import View
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta

class BitcoinTechnicalAnalysisAPI(APIView):
    """API کامل تحلیل تکنیکال بیت‌کوین با 15 اندیکاتور مهم"""
    
    CACHE_KEY = 'bitcoin_ta_analysis'
    CACHE_TIMEOUT = 3600  # 1 ساعت
    
    def get(self, request):
        try:
            # بررسی کش
            cached_data = cache.get(self.CACHE_KEY)
            if cached_data:
                return Response(cached_data)
            
            # دریافت و پردازش داده‌ها
            df = self.fetch_market_data()
            analysis = self.complete_technical_analysis(df)
            
            # ذخیره در کش
            cache.set(self.CACHE_KEY, analysis, self.CACHE_TIMEOUT)
            
            return Response(analysis)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # return JsonResponse(
            #     {'error': f'خطا در پردازش داده‌ها: {str(e)}'},
            #     status=500
            # )

    def fetch_market_data(self):
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

    def complete_technical_analysis(self, df):
        """محاسبه کامل تحلیل تکنیکال با 15 اندیکاتور مهم"""
        
        # 1. محاسبه اندیکاتورهای روند
        df['sma20'] = SMAIndicator(close=df['price'], window=20).sma_indicator()
        df['sma50'] = SMAIndicator(close=df['price'], window=50).sma_indicator()
        df['sma200'] = SMAIndicator(close=df['price'], window=200).sma_indicator()
        df['ema12'] = EMAIndicator(close=df['price'], window=12).ema_indicator()
        df['ema26'] = EMAIndicator(close=df['price'], window=26).ema_indicator()
        
        # 2. محاسبه MACD
        macd = MACD(close=df['price'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()
        
        # 3. محاسبه RSI
        df['rsi14'] = RSIIndicator(close=df['price'], window=14).rsi()
        
        # 4. محاسبه بولینگر باندز
        bb = BollingerBands(close=df['price'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # 5. محاسبه استوکاستیک
        stoch = StochasticOscillator(
            high=df['price'], low=df['price'], close=df['price'], 
            window=14, smooth_window=3
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # 6. محاسبه ATR
        df['atr14'] = ATR(
            high=df['price'], low=df['price'], close=df['price'], 
            window=14
        ).average_true_range()
        
        # 7. محاسبه ADX
        adx = ADXIndicator(
            high=df['price'], low=df['price'], close=df['price'], 
            window=14
        )
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()
        
        # 8. محاسبه ایچیموکو
        ichimoku = IchimokuIndicator(
            high=df['price'], low=df['price'], 
            window1=9, window2=26, window3=52
        )
        df['ichi_conv'] = ichimoku.ichimoku_conversion_line()
        df['ichi_base'] = ichimoku.ichimoku_base_line()
        df['ichi_a'] = ichimoku.ichimoku_a()
        df['ichi_b'] = ichimoku.ichimoku_b()
        
        # 9. محاسبه MFI (اگر حجم معاملات موجود باشد)
        if 'volume' in df.columns:
            df['mfi14'] = MFIIndicator(
                high=df['price'], low=df['price'], 
                close=df['price'], volume=df['volume'], 
                window=14
            ).money_flow_index()
        
        # 10. محاسبه پارابولیک SAR
        df['psar'] = PSARIndicator(
            high=df['price'], low=df['price'], 
            close=df['price'], step=0.02, max_step=0.2
        ).psar()
        
        # 11. محاسبه CCI
        df['cci20'] = CCIIndicator(
            high=df['price'], low=df['price'], 
            close=df['price'], window=20
        ).cci()
        
        # 12. محاسبه Williams %R
        df['williams14'] = WilliamsRIndicator(
            high=df['price'], low=df['price'], 
            close=df['price'], lbp=14
        ).williams_r()
        
        # 13. محاسبه Accumulation/Distribution
        if 'volume' in df.columns:
            df['adl'] = AccDistIndexIndicator(
                high=df['price'], low=df['price'], 
                close=df['price'], volume=df['volume']
            ).acc_dist_index()
        
        # تحلیل نهایی
        return self.generate_analysis_report(df)

    def generate_analysis_report(self, df):
        """تولید گزارش تحلیلی از داده‌های محاسبه شده"""
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        # تعیین روند کلی
        price_trend = self.determine_trend(last_row['price'], prev_row['price'])
        
        # گزارش کامل
        report = {
            'price': {
                'value': round(last_row['price'], 2),
                'trend': price_trend,
                'position': self.get_price_position(last_row)
            },
            'trend_indicators': {
                'sma': {
                    'sma20': self.get_ma_analysis(last_row, 'sma20'),
                    'sma50': self.get_ma_analysis(last_row, 'sma50'),
                    'sma200': self.get_ma_analysis(last_row, 'sma200'),
                    'golden_cross': self.check_cross(df, 'sma50', 'sma200'),
                    'death_cross': self.check_cross(df, 'sma200', 'sma50')
                },
                'ema': {
                    'ema12': self.get_ma_analysis(last_row, 'ema12'),
                    'ema26': self.get_ma_analysis(last_row, 'ema26'),
                    'ema_cross': self.check_cross(df, 'ema12', 'ema26')
                },
                'ichimoku': self.analyze_ichimoku(last_row),
                'adx': self.analyze_adx(last_row)
            },
            'momentum_indicators': {
                'macd': self.analyze_macd(last_row, prev_row),
                'rsi': self.analyze_rsi(last_row),
                'stochastic': self.analyze_stochastic(last_row),
                'cci': self.analyze_cci(last_row),
                'williams': self.analyze_williams(last_row)
            },
            'volatility_indicators': {
                'bollinger_bands': self.analyze_bollinger(last_row),
                'atr': self.analyze_atr(last_row, prev_row)
            },
            'volume_indicators': {
                'mfi': self.analyze_mfi(last_row) if 'mfi14' in last_row else None,
                'adl': self.analyze_adl(last_row, prev_row) if 'adl' in last_row else None
            },
            'other_indicators': {
                'psar': self.analyze_psar(last_row, prev_row)
            },
            'metadata': {
                'last_updated': pd.Timestamp.now().isoformat(),
                'timeframe': 'daily',
                'indicators_count': 15,
                'data_points': len(df)
            }
        }
        
        return report

    # ----- متدهای کمکی تحلیل -----
    
    @staticmethod
    def determine_trend(current, previous):
        """تعیین روند صعودی/نزولی"""
        return 'up' if current > previous else 'down'
    
    def get_price_position(self, row):
        """تعیین موقعیت قیمت نسبت به اندیکاتورها"""
        position = {
            'bollinger': 'inside',
            'ichimoku': 'inside'
        }
        
        # موقعیت نسبت به بولینگر باندز
        if row['price'] > row['bb_upper']:
            position['bollinger'] = 'above_upper'
        elif row['price'] < row['bb_lower']:
            position['bollinger'] = 'below_lower'
        
        # موقعیت نسبت به ابر ایچیموکو
        cloud_top = max(row['ichi_a'], row['ichi_b'])
        cloud_bottom = min(row['ichi_a'], row['ichi_b'])
        
        if row['price'] > cloud_top:
            position['ichimoku'] = 'above_cloud'
        elif row['price'] < cloud_bottom:
            position['ichimoku'] = 'below_cloud'
        
        return position
    
    def get_ma_analysis(self, row, ma_key):
        """تحلیل میانگین متحرک"""
        return {
            'value': round(row[ma_key], 2),
            'trend': self.determine_trend(row[ma_key], row[ma_key]),
            'relation_to_price': 'above' if row[ma_key] > row['price'] else 'below'
        }
    
    def check_cross(self, df, fast_key, slow_key):
        """بررسی وقوع کراس"""
        current_fast = df[fast_key].iloc[-1]
        current_slow = df[slow_key].iloc[-1]
        prev_fast = df[fast_key].iloc[-2]
        prev_slow = df[slow_key].iloc[-2]
        
        return {
            'occurred': str(current_fast > current_slow and prev_fast <= prev_slow),
            'current_diff': round(current_fast - current_slow, 2),
            'trend': 'bullish' if current_fast > current_slow else 'bearish'
        }
    
    def analyze_macd(self, row, prev_row):
        """تحلیل MACD"""
        return {
            'macd_line': round(row['macd'], 2),
            'signal_line': round(row['macd_signal'], 2),
            'histogram': round(row['macd_hist'], 2),
            'trend': 'bullish' if row['macd'] > row['macd_signal'] else 'bearish',
            'momentum': 'increasing' if row['macd_hist'] > prev_row['macd_hist'] else 'decreasing'
        }
    
    def analyze_rsi(self, row):
        """تحلیل RSI"""
        return {
            'value': round(row['rsi14'], 2),
            'trend': self.determine_trend(row['rsi14'], row['rsi14']),
            'status': 'overbought' if row['rsi14'] > 70 else 
                     'oversold' if row['rsi14'] < 30 else 'neutral'
        }
    
    def analyze_bollinger(self, row):
        """تحلیل بولینگر باندز"""
        return {
            'upper': round(row['bb_upper'], 2),
            'middle': round(row['bb_middle'], 2),
            'lower': round(row['bb_lower'], 2),
            'width': round(row['bb_width'], 4),
            'price_position': 'above' if row['price'] > row['bb_upper'] else 
                            'below' if row['price'] < row['bb_lower'] else 'inside',
            'squeeze': 'yes' if row['bb_width'] < 0.05 else 'no'
        }
    
    def analyze_stochastic(self, row):
        """تحلیل استوکاستیک"""
        return {
            'k_line': round(row['stoch_k'], 2),
            'd_line': round(row['stoch_d'], 2),
            'trend': 'bullish' if row['stoch_k'] > row['stoch_d'] else 'bearish',
            'status': 'overbought' if row['stoch_k'] > 80 else 
                     'oversold' if row['stoch_k'] < 20 else 'neutral'
        }
    
    def analyze_adx(self, row):
        """تحلیل ADX"""
        return {
            'adx': round(row['adx'], 2),
            'pos_di': round(row['adx_pos'], 2),
            'neg_di': round(row['adx_neg'], 2),
            'trend_strength': 'strong' if row['adx'] > 25 else 'weak',
            'trend_direction': 'up' if row['adx_pos'] > row['adx_neg'] else 'down'
        }
    
    def analyze_ichimoku(self, row):
        """تحلیل ایچیموکو"""
        return {
            'conversion': round(row['ichi_conv'], 2),
            'base': round(row['ichi_base'], 2),
            'span_a': round(row['ichi_a'], 2),
            'span_b': round(row['ichi_b'], 2),
            'cloud_color': 'green' if row['ichi_a'] > row['ichi_b'] else 'red',
            'cloud_position': 'above' if row['price'] > max(row['ichi_a'], row['ichi_b']) else 
                             'below' if row['price'] < min(row['ichi_a'], row['ichi_b']) else 'inside'
        }
    
    def analyze_mfi(self, row):
        """تحلیل MFI"""
        return {
            'value': round(row['mfi14'], 2),
            'status': 'overbought' if row['mfi14'] > 80 else 
                     'oversold' if row['mfi14'] < 20 else 'neutral'
        }
    
    def analyze_atr(self, row, prev_row):
        """تحلیل ATR"""
        return {
            'value': round(row['atr14'], 2),
            'trend': 'increasing' if row['atr14'] > prev_row['atr14'] else 'decreasing',
            'volatility': 'high' if row['atr14'] > 0.02 * row['price'] else 'low'
        }
    
    def analyze_cci(self, row):
        """تحلیل CCI"""
        return {
            'value': round(row['cci20'], 2),
            'status': 'overbought' if row['cci20'] > 100 else 
                     'oversold' if row['cci20'] < -100 else 'neutral'
        }
    
    def analyze_williams(self, row):
        """تحلیل Williams %R"""
        return {
            'value': round(row['williams14'], 2),
            'status': 'overbought' if row['williams14'] > -20 else 
                     'oversold' if row['williams14'] < -80 else 'neutral'
        }
    
    def analyze_psar(self, row, prev_row):
        """تحلیل پارابولیک SAR"""
        return {
            'value': round(row['psar'], 2),
            'trend': 'up' if row['psar'] < row['price'] else 'down',
            'reversal': 'yes' if (row['psar'] < row['price'] and prev_row['psar'] > prev_row['price']) or 
                       (row['psar'] > row['price'] and prev_row['psar'] < prev_row['price']) else 'no'
        }
    
    def analyze_adl(self, row, prev_row):
        """تحلیل Accumulation/Distribution"""
        return {
            'value': round(row['adl'], 2),
            'trend': 'up' if row['adl'] > prev_row['adl'] else 'down'
        }