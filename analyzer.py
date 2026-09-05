import pandas as pd
import numpy as np
import ta

class StockAnalyzer:
    def __init__(self):
        pass
    
    def technical_analysis(self, stock_data):
        """Perform technical analysis on stock data"""
        try:
            latest_data = stock_data.iloc[-1]
            
            # RSI Analysis
            rsi = latest_data['RSI']
            rsi_signal = self.get_rsi_signal(rsi)
            
            # MACD Analysis
            macd_line, macd_signal, macd_histogram = self.calculate_macd(stock_data['Close'])
            macd_signal_trend = "Bullish" if macd_line.iloc[-1] > macd_signal.iloc[-1] else "Bearish"
            
            # Moving Average Analysis
            ma_20 = latest_data['MA_20']
            ma_50 = latest_data['MA_50']
            current_price = latest_data['Close']
            
            ma_trend = 1 if ma_20 > ma_50 and current_price > ma_20 else -1
            
            # Bollinger Bands
            bb_upper, bb_lower = self.calculate_bollinger_bands(stock_data['Close'])
            bb_signal = self.get_bollinger_signal(current_price, bb_upper.iloc[-1], bb_lower.iloc[-1])
            
            # Support and Resistance
            support, resistance = self.calculate_support_resistance(stock_data)
            
            # Volume Analysis
            volume_trend = self.analyze_volume_trend(stock_data)
            
            return {
                'rsi': rsi,
                'rsi_signal': rsi_signal,
                'macd': macd_line.iloc[-1],
                'macd_signal': macd_signal.iloc[-1],
                'macd_trend': macd_signal_trend,
                'ma_trend': ma_trend,
                'ma_20': ma_20,
                'ma_50': ma_50,
                'bollinger_signal': bb_signal,
                'support': support,
                'resistance': resistance,
                'volume_trend': volume_trend,
                'technical_score': self.calculate_technical_score({
                    'rsi': rsi,
                    'macd_trend': macd_signal_trend,
                    'ma_trend': ma_trend,
                    'bollinger_signal': bb_signal
                })
            }
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {}
    
    def fundamental_analysis(self, fundamental_data):
        """Analyze fundamental metrics"""
        try:
            # Valuation Analysis
            pe_score = self.score_pe_ratio(fundamental_data.get('pe_ratio', 0))
            pb_score = self.score_pb_ratio(fundamental_data.get('pb_ratio', 0))
            
            # Profitability Analysis
            roe_score = self.score_roe(fundamental_data.get('roe', 0))
            roa_score = self.score_roa(fundamental_data.get('roa', 0))
            margin_score = self.score_margin(fundamental_data.get('net_margin', 0))
            
            # Growth Analysis
            revenue_growth_score = self.score_growth(fundamental_data.get('revenue_growth', 0))
            profit_growth_score = self.score_growth(fundamental_data.get('profit_growth', 0))
            
            # Financial Health
            debt_score = self.score_debt_ratio(fundamental_data.get('debt_equity', 0))
            
            # Overall Fundamental Score
            fundamental_score = np.mean([
                pe_score, pb_score, roe_score, roa_score, 
                margin_score, revenue_growth_score, profit_growth_score, debt_score
            ])
            
            return {
                'pe_ratio': fundamental_data.get('pe_ratio', 0),
                'pb_ratio': fundamental_data.get('pb_ratio', 0),
                'ev_ebitda': fundamental_data.get('ev_ebitda', 0),
                'roe': fundamental_data.get('roe', 0),
                'roa': fundamental_data.get('roa', 0),
                'net_margin': fundamental_data.get('net_margin', 0),
                'revenue_growth': fundamental_data.get('revenue_growth', 0),
                'profit_growth': fundamental_data.get('profit_growth', 0),
                'debt_equity': fundamental_data.get('debt_equity', 0),
                'fundamental_score': fundamental_score,
                'valuation_score': np.mean([pe_score, pb_score]),
                'profitability_score': np.mean([roe_score, roa_score, margin_score]),
                'growth_score': np.mean([revenue_growth_score, profit_growth_score]),
                'financial_health_score': debt_score
            }
            
        except Exception as e:
            print(f"Error in fundamental analysis: {e}")
            return {}
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        return macd_line, macd_signal, macd_histogram
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band
    
    def calculate_support_resistance(self, stock_data, lookback=20):
        """Calculate support and resistance levels"""
        try:
            recent_data = stock_data.tail(lookback)
            support = recent_data['Low'].min()
            resistance = recent_data['High'].max()
            return support, resistance
        except:
            return 0, 0
    
    def analyze_volume_trend(self, stock_data, window=10):
        """Analyze volume trend"""
        try:
            recent_volume = stock_data['Volume'].tail(window).mean()
            historical_volume = stock_data['Volume'].tail(50).mean()
            
            if recent_volume > historical_volume * 1.2:
                return "High"
            elif recent_volume < historical_volume * 0.8:
                return "Low"
            else:
                return "Normal"
        except:
            return "Normal"
    
    # Scoring functions
    def get_rsi_signal(self, rsi):
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    def get_bollinger_signal(self, price, upper, lower):
        if price > upper:
            return "Overbought"
        elif price < lower:
            return "Oversold"
        else:
            return "Neutral"
    
    def score_pe_ratio(self, pe):
        if pe <= 0:
            return 0
        elif pe < 15:
            return 8
        elif pe < 25:
            return 6
        elif pe < 35:
            return 4
        else:
            return 2
    
    def score_pb_ratio(self, pb):
        if pb <= 0:
            return 0
        elif pb < 1:
            return 9
        elif pb < 3:
            return 7
        elif pb < 5:
            return 5
        else:
            return 3
    
    def score_roe(self, roe):
        if roe > 20:
            return 9
        elif roe > 15:
            return 7
        elif roe > 10:
            return 5
        elif roe > 5:
            return 3
        else:
            return 1
    
    def score_roa(self, roa):
        if roa > 15:
            return 9
        elif roa > 10:
            return 7
        elif roa > 5:
            return 5
        elif roa > 2:
            return 3
        else:
            return 1
    
    def score_margin(self, margin):
        if margin > 20:
            return 9
        elif margin > 15:
            return 7
        elif margin > 10:
            return 5
        elif margin > 5:
            return 3
        else:
            return 1
    
    def score_growth(self, growth):
        if growth > 25:
            return 9
        elif growth > 15:
            return 7
        elif growth > 10:
            return 5
        elif growth > 5:
            return 3
        elif growth > 0:
            return 2
        else:
            return 1
    
    def score_debt_ratio(self, debt_ratio):
        if debt_ratio < 0.3:
            return 9
        elif debt_ratio < 0.5:
            return 7
        elif debt_ratio < 1:
            return 5
        elif debt_ratio < 2:
            return 3
        else:
            return 1
    
    def calculate_technical_score(self, technical_indicators):
        """Calculate overall technical score"""
        score = 5  # Base score
        
        # RSI contribution
        rsi = technical_indicators.get('rsi', 50)
        if 30 <= rsi <= 70:
            score += 1
        elif rsi < 30:
            score += 2  # Oversold - potential buy
        elif rsi > 70:
            score -= 1  # Overbought
        
        # MACD contribution
        if technical_indicators.get('macd_trend') == "Bullish":
            score += 1
        else:
            score -= 1
        
        # MA Trend contribution
        if technical_indicators.get('ma_trend', 0) > 0:
            score += 1
        else:
            score -= 1
        
        # Bollinger Bands contribution
        bb_signal = technical_indicators.get('bollinger_signal', 'Neutral')
        if bb_signal == "Oversold":
            score += 1
        elif bb_signal == "Overbought":
            score -= 1
        
        return max(0, min(10, score))  # Clamp between 0 and 10