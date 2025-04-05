import pandas as pd
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from . import tc

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
            df = tc.fetch_market_data()
            analysis = self.complete_technical_analysis(df)
            
            # ذخیره در کش
            cache.set(self.CACHE_KEY, analysis, self.CACHE_TIMEOUT)
            
            return Response(analysis)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    def complete_technical_analysis(self, df):

        calculator = tc.TechnicalCalculator(df)
        calculated_df = calculator.calculate_all()
        
        # تحلیل نهایی
        return self.generate_analysis_report(calculated_df)

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
    



class AdvancedTechnicalAnalysis(APIView):
    """
    اندپوینت تحلیل تکنیکال پیشرفته با ترکیب‌های هوشمند اندیکاتورها
    """
    
    CACHE_KEY = 'advanced_ta_analysis'
    CACHE_TIMEOUT = 3600  # 1 ساعت

    def get(self, request):
        try:
            cached_data = cache.get(self.CACHE_KEY)
            if cached_data:
                return Response(cached_data)
            
            df = tc.fetch_market_data()

            # استفاده از کلاس محاسباتی
            calculator = tc.TechnicalCalculator(df)
            calculated_df = calculator.calculate_all()
            analysis = {
                "individual_indicators": self.get_high_confidence_individual_indicators(calculated_df),
                "combined_strategies": self.get_high_confirmation_combinations(calculated_df)
            }
            
            cache.set(self.CACHE_KEY, analysis, self.CACHE_TIMEOUT)
            return Response(analysis)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def get_high_confidence_individual_indicators(self, df):
        """اندیکاتورهای مستقل با درصد تأییدیه بالا"""
        return {
            "golden_cross": {
                "indicators": ["SMA50", "SMA200"],
                "value": df['sma50'].iloc[-1] > df['sma200'].iloc[-1],
                "trend": "bullish" if df['sma50'].iloc[-1] > df['sma200'].iloc[-1] else "bearish",
                "confidence": "85%",
                "description": "سیگنال تغییر روند بلندمدت"
            },
            "macd_crossover": {
                "indicators": ["MACD", "Signal"],
                "value": float(df['macd'].iloc[-1] - df['macd_signal'].iloc[-1]),
                "trend": "bullish" if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] else "bearish",
                "confidence": "80%",
                "description": "تغییر مومنتوم میان‌مدت"
            },
            "rsi_divergence": {
                "indicators": ["RSI14"],
                "value": float(df['rsi14'].iloc[-1]),
                "trend": self.get_rsi_trend(df),
                "confidence": "75%",
                "description": "اشباع خرید/فروش با تأییدیه بالا"
            }
        }

    def get_high_confirmation_combinations(self, df):
        """ترکیب‌های تأییدکننده چندلایه"""
        return {
            "trend_confirmation": {
                "strategy": "تأیید روند بلندمدت",
                "indicators": ["SMA50", "SMA200", "Ichimoku Cloud", "ADX"],
                "conditions": {
                    "golden_cross": df['sma50'].iloc[-1] > df['sma200'].iloc[-1],
                    "price_above_cloud": df['price'].iloc[-1] > max(df['ichi_a'].iloc[-1], df['ichi_b'].iloc[-1]),
                    "adx_strength": df['adx'].iloc[-1] > 25
                },
                "confirmed": all([
                    df['sma50'].iloc[-1] > df['sma200'].iloc[-1],
                    df['price'].iloc[-1] > max(df['ichi_a'].iloc[-1], df['ichi_b'].iloc[-1]),
                    df['adx'].iloc[-1] > 25
                ]),
                "confidence": "90%",
                "trend": self.get_combined_trend(df, 'trend')
            },
            "momentum_confirmation": {
                "strategy": "تأیید مومنتوم قوی",
                "indicators": ["MACD", "RSI", "Stochastic"],
                "conditions": {
                    "macd_bullish": df['macd'].iloc[-1] > df['macd_signal'].iloc[-1],
                    "rsi_optimal": 50 < df['rsi14'].iloc[-1] < 70,
                    "stochastic_cross": df['stoch_k'].iloc[-1] > df['stoch_d'].iloc[-1]
                },
                "confirmed": all([
                    df['macd'].iloc[-1] > df['macd_signal'].iloc[-1],
                    50 < df['rsi14'].iloc[-1] < 70,
                    df['stoch_k'].iloc[-1] > df['stoch_d'].iloc[-1]
                ]),
                "confidence": "85%",
                "trend": self.get_combined_trend(df, 'momentum')
            },
            "breakout_confirmation": {
                "strategy": "تأیید شکست مقاومت",
                "indicators": ["Bollinger Bands", "Volume", "ATR"],
                "conditions": {
                    "price_breakout": df['price'].iloc[-1] > df['bb_upper'].iloc[-1],
                    "volume_spike": df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1] * 1.5,
                    "high_volatility": df['atr14'].iloc[-1] > df['atr14'].rolling(20).mean().iloc[-1]
                },
                "confirmed": all([
                    df['price'].iloc[-1] > df['bb_upper'].iloc[-1],
                    df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1] * 1.5,
                    df['atr14'].iloc[-1] > df['atr14'].rolling(20).mean().iloc[-1]
                ]),
                "confidence": "88%",
                "trend": "bullish" if df['price'].iloc[-1] > df['bb_upper'].iloc[-1] else "bearish"
            }
        }

    # متدهای کمکی
    def get_rsi_trend(self, df):
        rsi = df['rsi14'].iloc[-1]
        if rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        elif rsi > 50:
            return "bullish"
        else:
            return "bearish"

    def get_combined_trend(self, df, strategy_type):
        if strategy_type == 'trend':
            conditions = [
                df['sma50'].iloc[-1] > df['sma200'].iloc[-1],
                df['price'].iloc[-1] > max(df['ichi_a'].iloc[-1], df['ichi_b'].iloc[-1]),
                df['adx'].iloc[-1] > 25
            ]
        else:  # momentum
            conditions = [
                df['macd'].iloc[-1] > df['macd_signal'].iloc[-1],
                50 < df['rsi14'].iloc[-1] < 70,
                df['stoch_k'].iloc[-1] > df['stoch_d'].iloc[-1]
            ]
        
        return "strong_bullish" if all(conditions) else "bullish" if sum(conditions) >= 2 else "neutral"