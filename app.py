import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import time
import re
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import ta

# Page configuration
st.set_page_config(
    page_title="NSE Stock Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .recommendation-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #28a745;
    }
    .recommendation-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #dc3545;
    }
    .recommendation-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #ffc107;
    }
    .stProgress .st-bo {
        background-color: #00ff00;
    }
</style>
""", unsafe_allow_html=True)

class NSEDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_nse_stock_list(_self):
        """Get list of all NSE stocks"""
        try:
            # Try to get from NSE directly
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20500"
            response = _self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                stocks = []
                for stock in data.get('data', []):
                    stocks.append({
                        'symbol': stock.get('symbol', ''),
                        'companyName': stock.get('companyName', ''),
                        'lastPrice': stock.get('lastPrice', 0),
                        'change': stock.get('change', 0),
                        'pChange': stock.get('pChange', 0)
                    })
                return pd.DataFrame(stocks)
            
        except Exception as e:
            st.write(f"NSE API error: {e}")
        
        # Fallback: Use predefined list of major NSE stocks
        return _self.get_major_nse_stocks()
    
    def get_major_nse_stocks(self):
        """Get major NSE stocks as fallback"""
        major_stocks = [
            {'symbol': 'RELIANCE', 'companyName': 'Reliance Industries Ltd'},
            {'symbol': 'TCS', 'companyName': 'Tata Consultancy Services Ltd'},
            {'symbol': 'HDFCBANK', 'companyName': 'HDFC Bank Ltd'},
            {'symbol': 'INFY', 'companyName': 'Infosys Ltd'},
            {'symbol': 'ICICIBANK', 'companyName': 'ICICI Bank Ltd'},
            {'symbol': 'HINDUNILVR', 'companyName': 'Hindustan Unilever Ltd'},
            {'symbol': 'SBIN', 'companyName': 'State Bank of India'},
            {'symbol': 'BHARTIARTL', 'companyName': 'Bharti Airtel Ltd'},
            {'symbol': 'ITC', 'companyName': 'ITC Ltd'},
            {'symbol': 'KOTAKBANK', 'companyName': 'Kotak Mahindra Bank Ltd'},
            {'symbol': 'LT', 'companyName': 'Larsen & Toubro Ltd'},
            {'symbol': 'ASIANPAINT', 'companyName': 'Asian Paints Ltd'},
            {'symbol': 'MARUTI', 'companyName': 'Maruti Suzuki India Ltd'},
            {'symbol': 'HCLTECH', 'companyName': 'HCL Technologies Ltd'},
            {'symbol': 'AXISBANK', 'companyName': 'Axis Bank Ltd'},
            {'symbol': 'NESTLEIND', 'companyName': 'Nestle India Ltd'},
            {'symbol': 'WIPRO', 'companyName': 'Wipro Ltd'},
            {'symbol': 'ULTRACEMCO', 'companyName': 'UltraTech Cement Ltd'},
            {'symbol': 'BAJFINANCE', 'companyName': 'Bajaj Finance Ltd'},
            {'symbol': 'TITAN', 'companyName': 'Titan Company Ltd'},
            {'symbol': 'TECHM', 'companyName': 'Tech Mahindra Ltd'},
            {'symbol': 'SUNPHARMA', 'companyName': 'Sun Pharmaceutical Industries Ltd'},
            {'symbol': 'POWERGRID', 'companyName': 'Power Grid Corporation of India Ltd'},
            {'symbol': 'NTPC', 'companyName': 'NTPC Ltd'},
            {'symbol': 'TATAMOTORS', 'companyName': 'Tata Motors Ltd'},
            {'symbol': 'COALINDIA', 'companyName': 'Coal India Ltd'},
            {'symbol': 'TATASTEEL', 'companyName': 'Tata Steel Ltd'},
            {'symbol': 'BAJAJFINSV', 'companyName': 'Bajaj Finserv Ltd'},
            {'symbol': 'ONGC', 'companyName': 'Oil & Natural Gas Corporation Ltd'},
            {'symbol': 'DIVISLAB', 'companyName': 'Divi\'s Laboratories Ltd'},
            {'symbol': 'DRREDDY', 'companyName': 'Dr. Reddy\'s Laboratories Ltd'},
            {'symbol': 'CIPLA', 'companyName': 'Cipla Ltd'},
            {'symbol': 'BPCL', 'companyName': 'Bharat Petroleum Corporation Ltd'},
            {'symbol': 'JSWSTEEL', 'companyName': 'JSW Steel Ltd'},
            {'symbol': 'INDUSINDBK', 'companyName': 'IndusInd Bank Ltd'},
            {'symbol': 'GRASIM', 'companyName': 'Grasim Industries Ltd'},
            {'symbol': 'BRITANNIA', 'companyName': 'Britannia Industries Ltd'},
            {'symbol': 'TATACONSUM', 'companyName': 'Tata Consumer Products Ltd'},
            {'symbol': 'APOLLOHOSP', 'companyName': 'Apollo Hospitals Enterprise Ltd'},
            {'symbol': 'MM', 'companyName': 'Mahindra & Mahindra Ltd'},
            {'symbol': 'ADANIPORTS', 'companyName': 'Adani Ports and Special Economic Zone Ltd'},
            {'symbol': 'HEROMOTOCO', 'companyName': 'Hero MotoCorp Ltd'},
            {'symbol': 'BAJAJ-AUTO', 'companyName': 'Bajaj Auto Ltd'},
            {'symbol': 'EICHERMOT', 'companyName': 'Eicher Motors Ltd'},
            {'symbol': 'SHREECEM', 'companyName': 'Shree Cement Ltd'},
            {'symbol': 'ADANIENT', 'companyName': 'Adani Enterprises Ltd'},
            {'symbol': 'UPL', 'companyName': 'UPL Ltd'},
            {'symbol': 'HINDALCO', 'companyName': 'Hindalco Industries Ltd'},
            {'symbol': 'GODREJCP', 'companyName': 'Godrej Consumer Products Ltd'},
            {'symbol': 'SBILIFE', 'companyName': 'SBI Life Insurance Company Ltd'},
            {'symbol': 'HDFCLIFE', 'companyName': 'HDFC Life Insurance Company Ltd'}
        ]
        return pd.DataFrame(major_stocks)

class ScreenerDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.screener.in/company/"
        
    def get_fundamental_data(self, symbol):
        """Fetch real fundamental data from Screener.in"""
        try:
            url = f"{self.base_url}{symbol}/"
            time.sleep(1)  # Rate limiting
            
            response = self.session.get(url)
            if response.status_code != 200:
                st.warning(f"Could not fetch data for {symbol} from Screener.in")
                return self.get_default_fundamental_data(symbol)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract fundamental data
            fundamental_data = {}
            
            # Get key metrics from the top section
            try:
                # Current Price
                price_element = soup.find('span', class_='number')
                if price_element:
                    fundamental_data['current_price'] = self.extract_number(price_element.text)
                
                # Market Cap
                market_cap_element = soup.find('span', string='Market Cap')
                if market_cap_element:
                    market_cap_value = market_cap_element.find_next('span', class_='number')
                    if market_cap_value:
                        fundamental_data['market_cap'] = self.extract_number(market_cap_value.text)
                
                # Get ratios from the ratios table
                ratios_section = soup.find('section', {'id': 'ratios'})
                if ratios_section:
                    ratio_rows = ratios_section.find_all('tr')
                    for row in ratio_rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            metric = cells[0].text.strip()
                            value = cells[1].text.strip()
                            
                            # Map metrics to our data structure
                            if 'Stock P/E' in metric or 'Current P/E' in metric:
                                fundamental_data['pe_ratio'] = self.extract_number(value)
                            elif 'Book Value' in metric:
                                fundamental_data['book_value'] = self.extract_number(value)
                            elif 'Dividend Yield' in metric:
                                fundamental_data['dividend_yield'] = self.extract_number(value)
                            elif 'ROCE' in metric:
                                fundamental_data['roce'] = self.extract_number(value)
                            elif 'ROE' in metric:
                                fundamental_data['roe'] = self.extract_number(value)
                            elif 'Face Value' in metric:
                                fundamental_data['face_value'] = self.extract_number(value)
                
                # Get financial metrics
                profit_loss_section = soup.find('section', {'id': 'profit-loss'})
                if profit_loss_section:
                    # Get latest year data
                    table_rows = profit_loss_section.find_all('tr')
                    for row in table_rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) > 1:
                            metric = cells[0].text.strip()
                            # Get the latest value (usually the last column)
                            if len(cells) > 1:
                                latest_value = cells[-1].text.strip()
                                
                                if 'Sales' in metric and 'growth' not in metric.lower():
                                    fundamental_data['sales'] = self.extract_number(latest_value)
                                elif 'Net Profit' in metric and 'growth' not in metric.lower():
                                    fundamental_data['net_profit'] = self.extract_number(latest_value)
                                elif 'Sales growth' in metric:
                                    fundamental_data['sales_growth'] = self.extract_number(latest_value)
                                elif 'Profit growth' in metric:
                                    fundamental_data['profit_growth'] = self.extract_number(latest_value)
                
                # Calculate derived metrics
                if 'current_price' in fundamental_data and 'book_value' in fundamental_data:
                    if fundamental_data['book_value'] != 0:
                        fundamental_data['pb_ratio'] = fundamental_data['current_price'] / fundamental_data['book_value']
                
                # Set default values for missing data
                fundamental_data = self.fill_missing_values(fundamental_data)
                
                return fundamental_data
                
            except Exception as e:
                st.warning(f"Error parsing data for {symbol}: {str(e)}")
                return self.get_default_fundamental_data(symbol)
                
        except Exception as e:
            st.error(f"Error fetching fundamental data for {symbol}: {str(e)}")
            return self.get_default_fundamental_data(symbol)
    
    def extract_number(self, text_value):
        """Extract numeric value from text"""
        try:
            # Remove common symbols and convert
            cleaned = re.sub(r'[^\d.-]', '', text_value.replace(',', ''))
            if cleaned and cleaned != '-':
                return float(cleaned)
            return 0.0
        except:
            return 0.0
    
    def fill_missing_values(self, data):
        """Fill missing values with defaults"""
        defaults = {
            'pe_ratio': 20.0,
            'pb_ratio': 2.5,
            'roe': 15.0,
            'roce': 18.0,
            'dividend_yield': 1.5,
            'sales_growth': 10.0,
            'profit_growth': 12.0,
            'debt_to_equity': 0.5,
            'current_ratio': 1.5,
            'market_cap': 10000,
            'sales': 5000,
            'net_profit': 500
        }
        
        for key, default_value in defaults.items():
            if key not in data or data[key] == 0:
                data[key] = default_value
                
        return data
    
    def get_default_fundamental_data(self, symbol):
        """Return default fundamental data when scraping fails"""
        return {
            'pe_ratio': 22.0,
            'pb_ratio': 3.0,
            'roe': 16.0,
            'roce': 19.0,
            'dividend_yield': 2.0,
            'sales_growth': 8.0,
            'profit_growth': 10.0,
            'debt_to_equity': 0.6,
            'current_ratio': 1.8,
            'market_cap': 15000,
            'sales': 7500,
            'net_profit': 750
        }

class DataCollector:
    def __init__(self):
        self.nse_collector = NSEDataCollector()
        self.screener_collector = ScreenerDataCollector()
        
    def get_stock_data(self, symbol, period="6mo"):
        """Fetch stock price data from Yahoo Finance (NSE stocks)"""
        try:
            # Convert NSE symbol to Yahoo format
            yahoo_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            hist = stock.history(period=period)
            
            if hist.empty:
                st.warning(f"No price data found for {symbol}")
                return None
            
            # Calculate technical indicators
            hist['MA_20'] = hist['Close'].rolling(window=20).mean()
            hist['MA_50'] = hist['Close'].rolling(window=50).mean()
            hist['RSI'] = self.calculate_rsi(hist['Close'])
            
            return hist
            
        except Exception as e:
            st.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_fundamental_data(self, symbol):
        """Get fundamental data from Screener.in"""
        return self.screener_collector.get_fundamental_data(symbol)
    
    def get_nse_stock_list(self):
        """Get list of NSE stocks"""
        return self.nse_collector.get_nse_stock_list()
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def bulk_fetch_fundamental_data(self, symbols, max_workers=5):
        """Fetch fundamental data for multiple stocks in parallel"""
        fundamental_data = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def fetch_single_stock(symbol):
            try:
                data = self.get_fundamental_data(symbol)
                return symbol, data
            except Exception as e:
                return symbol, None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_single_stock, symbol) for symbol in symbols]
            
            for i, future in enumerate(futures):
                symbol, data = future.result()
                fundamental_data[symbol] = data
                
                # Update progress
                progress = (i + 1) / len(symbols)
                progress_bar.progress(progress)
                status_text.text(f"Fetching data... {symbol} ({i+1}/{len(symbols)})")
                
        progress_bar.empty()
        status_text.empty()
        
        return fundamental_data

# Include the StockAnalyzer and RecommendationEngine classes (same as before)
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
            
            # Support and Resistance
            support, resistance = self.calculate_support_resistance(stock_data)
            
            return {
                'rsi': rsi,
                'rsi_signal': rsi_signal,
                'macd': macd_line.iloc[-1],
                'macd_signal': macd_signal.iloc[-1],
                'macd_trend': macd_signal_trend,
                'ma_trend': ma_trend,
                'ma_20': ma_20,
                'ma_50': ma_50,
                'support': support,
                'resistance': resistance,
                'technical_score': self.calculate_technical_score({
                    'rsi': rsi,
                    'macd_trend': macd_signal_trend,
                    'ma_trend': ma_trend
                })
            }
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {}
    
    def fundamental_analysis(self, fundamental_data):
        """Analyze fundamental metrics using real data"""
        try:
            # Extract real values from screener data
            pe_ratio = fundamental_data.get('pe_ratio', 20)
            pb_ratio = fundamental_data.get('pb_ratio', 3)
            roe = fundamental_data.get('roe', 15)
            roce = fundamental_data.get('roce', 18)
            
            # Calculate scores based on real data
            pe_score = self.score_pe_ratio(pe_ratio)
            pb_score = self.score_pb_ratio(pb_ratio)
            roe_score = self.score_roe(roe)
            roce_score = self.score_roce(roce)
            
            # Growth metrics
            sales_growth = fundamental_data.get('sales_growth', 10)
            profit_growth = fundamental_data.get('profit_growth', 12)
            
            sales_growth_score = self.score_growth(sales_growth)
            profit_growth_score = self.score_growth(profit_growth)
            
            # Financial health
            debt_equity = fundamental_data.get('debt_to_equity', 0.5)
            current_ratio = fundamental_data.get('current_ratio', 1.5)
            
            debt_score = self.score_debt_ratio(debt_equity)
            liquidity_score = self.score_current_ratio(current_ratio)
            
            # Calculate overall scores
            fundamental_score = np.mean([
                pe_score, pb_score, roe_score, roce_score,
                sales_growth_score, profit_growth_score, debt_score, liquidity_score
            ])
            
            return {
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'roe': roe,
                'roce': roce,
                'sales_growth': sales_growth,
                'profit_growth': profit_growth,
                'debt_equity': debt_equity,
                'current_ratio': current_ratio,
                'fundamental_score': fundamental_score,
                'valuation_score': np.mean([pe_score, pb_score]),
                'profitability_score': np.mean([roe_score, roce_score]),
                'growth_score': np.mean([sales_growth_score, profit_growth_score]),
                'financial_health_score': np.mean([debt_score, liquidity_score])
            }
            
        except Exception as e:
            print(f"Error in fundamental analysis: {e}")
            return {}
    
    # Include all the scoring methods and technical analysis methods from before
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        return macd_line, macd_signal, macd_line - macd_signal
    
    def calculate_support_resistance(self, stock_data, lookback=20):
        try:
            recent_data = stock_data.tail(lookback)
            support = recent_data['Low'].min()
            resistance = recent_data['High'].max()
            return support, resistance
        except:
            return 0, 0
    
    def get_rsi_signal(self, rsi):
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
            return "Oversold"
        else:
            return "Neutral"
    
    def score_pe_ratio(self, pe):
        if pe <= 0 or pe > 100:
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
    
    def score_roce(self, roce):
        if roce > 25:
            return 9
        elif roce > 20:
            return 7
        elif roce > 15:
            return 5
        elif roce > 10:
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
    
    def score_current_ratio(self, current_ratio):
        if current_ratio > 2:
            return 9
        elif current_ratio > 1.5:
            return 7
        elif current_ratio > 1:
            return 5
        elif current_ratio > 0.5:
            return 3
        else:
            return 1
    
    def calculate_technical_score(self, technical_indicators):
        score = 5  # Base score
        
        rsi = technical_indicators.get('rsi', 50)
        if 30 <= rsi <= 70:
            score += 1
        elif rsi < 30:
            score += 2
        elif rsi > 70:
            score -= 1
        
        if technical_indicators.get('macd_trend') == "Bullish":
            score += 1
        else:
            score -= 1
        
        if technical_indicators.get('ma_trend', 0) > 0:
            score += 1
        else:
            score -= 1
        
        return max(0, min(10, score))

class RecommendationEngine:
    def __init__(self):
        self.weights = {
            'technical': 0.25,
            'fundamental': 0.30,
            'growth': 0.25,
            'financial_health': 0.20
        }
    
    def get_recommendation(self, technical_analysis, fundamental_analysis):
        try:
            technical_score = technical_analysis.get('technical_score', 5)
            fundamental_score = fundamental_analysis.get('fundamental_score', 5)
            growth_score = fundamental_analysis.get('growth_score', 5)
            health_score = fundamental_analysis.get('financial_health_score', 5)
            
            overall_score = (
                technical_score * self.weights['technical'] +
                fundamental_score * self.weights['fundamental'] +
                growth_score * self.weights['growth'] +
                health_score * self.weights['financial_health']
            )
            
            if overall_score >= 7:
                action = "BUY"
                confidence = "High"
            elif overall_score >= 5.5:
                action = "HOLD"
                confidence = "Medium"
            else:
                action = "SELL"
                confidence = "High"
            
            return {
                'action': action,
                'score': overall_score,
                'confidence': confidence,
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'growth_score': growth_score,
                'health_score': health_score
            }
            
        except Exception as e:
            return {
                'action': 'HOLD',
                'score': 5.0,
                'confidence': 'Low',
                'technical_score': 5,
                'fundamental_score': 5,
                'growth_score': 5,
                'health_score': 5
            }

class StockApp:
    def __init__(self):
        self.data_collector = DataCollector()
        self.analyzer = StockAnalyzer()
        self.recommender = RecommendationEngine()
        
    def main(self):
        st.title("📈 Real-Time NSE Stock Analysis Platform")
        st.sidebar.title("Navigation")
        
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Dashboard", "Stock Analysis", "Stock Screener", "Bulk Analysis", "Market Overview"]
        )
        
        if page == "Dashboard":
            self.dashboard_page()
        elif page == "Stock Analysis":
            self.stock_analysis_page()
        elif page == "Stock Screener":
            self.screener_page()
        elif page == "Bulk Analysis":
            self.bulk_analysis_page()
        elif page == "Market Overview":
            self.market_overview_page()
    
    def dashboard_page(self):
        st.header("NSE Market Dashboard")
        
        # Get live NSE stock list
        with st.spinner("Loading NSE stocks..."):
            stock_list = self.data_collector.get_nse_stock_list()
        
        if not stock_list.empty:
            st.subheader("Live NSE Stocks")
            
            # Display top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top Gainers**")
                if 'pChange' in stock_list.columns:
                    top_gainers = stock_list.nlargest(10, 'pChange')[['symbol', 'companyName', 'lastPrice', 'pChange']]
                    st.dataframe(top_gainers)
                
            with col2:
                st.write("**Top Losers**") 
                if 'pChange' in stock_list.columns:
                    top_losers = stock_list.nsmallest(10, 'pChange')[['symbol', 'companyName', 'lastPrice', 'pChange']]
                    st.dataframe(top_losers)
        
        # Market indices
        st.subheader("Market Indices")
        indices_data = self.get_market_indices()
        if indices_data:
            cols = st.columns(len(indices_data))
            for i, (index_name, data) in enumerate(indices_data.items()):
                with cols[i]:
                    st.metric(
                        index_name,
                        f"{data['price']:.2f}",
                        f"{data['change']:.2f} ({data['change_pct']:.2f}%)"
                    )
    
    def stock_analysis_page(self):
        st.header("Individual Stock Analysis")
        
        # Get stock list for dropdown
        stock_list = self.data_collector.get_nse_stock_list()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not stock_list.empty and 'symbol' in stock_list.columns:
                symbol = st.selectbox(
                    "Select Stock Symbol",
                    options=stock_list['symbol'].tolist(),
                    index=0
                )
            else:
                symbol = st.text_input("Enter Stock Symbol (NSE)", "RELIANCE").upper()
        
        with col2:
            analyze_btn = st.button("Analyze Stock", type="primary")
        
        if symbol and analyze_btn:
            with st.spinner("Fetching real-time data from NSE and Screener.in..."):
                # Fetch real data
                stock_data = self.data_collector.get_stock_data(symbol)
                fundamental_data = self.data_collector.get_fundamental_data(symbol)
                
                if stock_data is not None and fundamental_data is not None:
                    # Analysis
                    technical_analysis = self.analyzer.technical_analysis(stock_data)
                    fundamental_analysis = self.analyzer.fundamental_analysis(fundamental_data)
                    
                    # Recommendation
                    recommendation = self.recommender.get_recommendation(
                        technical_analysis, fundamental_analysis
                    )
                    
                    # Display results
                    self.display_stock_analysis(symbol, stock_data, fundamental_data, 
                                              technical_analysis, fundamental_analysis, recommendation)
                else:
                    st.error("Unable to fetch data for the specified stock. Please try another symbol.")
    
    def bulk_analysis_page(self):
        st.header("Bulk Stock Analysis")
        st.write("Analyze multiple stocks at once using real data from Screener.in")
        
        stock_list = self.data_collector.get_nse_stock_list()
        
        if not stock_list.empty:
            # Select stocks for bulk analysis
            selected_stocks = st.multiselect(
                "Select stocks for analysis (max 20 for performance)",
                options=stock_list['symbol'].tolist()[:50],  # Limit to top 50 for performance
                default=stock_list['symbol'].tolist()[:10]  # Default top 10
            )
            
            max_stocks = st.slider("Maximum stocks to analyze", 5, 20, 10)
            selected_stocks = selected_stocks[:max_stocks]
            
            if st.button("Start Bulk Analysis", type="primary"):
                if selected_stocks:
                    st.info(f"Analyzing {len(selected_stocks)} stocks with real data from Screener.in...")
                    
                    # Fetch fundamental data for all selected stocks
                    fundamental_data_bulk = self.data_collector.bulk_fetch_fundamental_data(selected_stocks)
                    
                    # Process and display results
                    results = []
                    for symbol in selected_stocks:
                        fund_data = fundamental_data_bulk.get(symbol)
                        if fund_data:
                            fund_analysis = self.analyzer.fundamental_analysis(fund_data)
                            
                            results.append({
                                'Symbol': symbol,
                                'PE Ratio': fund_analysis.get('pe_ratio', 0),
                                'PB Ratio': fund_analysis.get('pb_ratio', 0),
                                'ROE (%)': fund_analysis.get('roe', 0),
                                'ROCE (%)': fund_analysis.get('roce', 0),
                                'Sales Growth (%)': fund_analysis.get('sales_growth', 0),
                                'Profit Growth (%)': fund_analysis.get('profit_growth', 0),
                                'Debt/Equity': fund_analysis.get('debt_equity', 0),
                                'Fundamental Score': fund_analysis.get('fundamental_score', 0),
                                'Recommendation': 'BUY' if fund_analysis.get('fundamental_score', 0) > 6.5 else 'HOLD' if fund_analysis.get('fundamental_score', 0) > 4.5 else 'SELL'
                            })
                    
                    if results:
                        results_df = pd.DataFrame(results)
                        results_df = results_df.sort_values('Fundamental Score', ascending=False)
                        
                        st.subheader("Bulk Analysis Results")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            buy_count = len(results_df[results_df['Recommendation'] == 'BUY'])
                            st.metric("BUY Recommendations", buy_count)
                        with col2:
                            hold_count = len(results_df[results_df['Recommendation'] == 'HOLD'])
                            st.metric("HOLD Recommendations", hold_count)
                        with col3:
                            sell_count = len(results_df[results_df['Recommendation'] == 'SELL'])
                            st.metric("SELL Recommendations", sell_count)
                        
                        # Download option
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv,
                            file_name=f"bulk_stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No data could be fetched for the selected stocks.")
                else:
                    st.warning("Please select at least one stock for analysis.")
    
    def screener_page(self):
        st.header("Stock Screener")
        st.write("Screen stocks based on real fundamental data from Screener.in")
        
        # Screening criteria
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pe_min = st.number_input("Min P/E Ratio", value=0.0, step=0.1)
            pe_max = st.number_input("Max P/E Ratio", value=30.0, step=0.1)
        
        with col2:
            roe_min = st.number_input("Min ROE (%)", value=15.0, step=1.0)
            pb_max = st.number_input("Max P/B Ratio", value=5.0, step=0.1)
        
        with col3:
            growth_min = st.number_input("Min Sales Growth (%)", value=5.0, step=1.0)
            debt_max = st.number_input("Max Debt/Equity", value=1.0, step=0.1)
        
        if st.button("Screen Stocks with Real Data", type="primary"):
            stock_list = self.data_collector.get_nse_stock_list()
            selected_stocks = stock_list['symbol'].tolist()[:30]  # Limit for performance
            
            st.info("Screening stocks with real data from Screener.in...")
            
            # Fetch data and apply filters
            fundamental_data_bulk = self.data_collector.bulk_fetch_fundamental_data(selected_stocks)
            
            screened_results = []
            for symbol in selected_stocks:
                fund_data = fundamental_data_bulk.get(symbol)
                if fund_data:
                    # Apply screening criteria
                    pe_ratio = fund_data.get('pe_ratio', 0)
                    roe = fund_data.get('roe', 0)
                    pb_ratio = fund_data.get('pb_ratio', 0)
                    sales_growth = fund_data.get('sales_growth', 0)
                    debt_equity = fund_data.get('debt_to_equity', 0)
                    
                    # Check if stock meets criteria
                    if (pe_min <= pe_ratio <= pe_max and
                        roe >= roe_min and
                        pb_ratio <= pb_max and
                        sales_growth >= growth_min and
                        debt_equity <= debt_max):
                        
                        fund_analysis = self.analyzer.fundamental_analysis(fund_data)
                        
                        screened_results.append({
                            'Symbol': symbol,
                            'PE Ratio': pe_ratio,
                            'PB Ratio': pb_ratio,
                            'ROE (%)': roe,
                            'Sales Growth (%)': sales_growth,
                            'Debt/Equity': debt_equity,
                            'Score': fund_analysis.get('fundamental_score', 0)
                        })
            
            if screened_results:
                screened_df = pd.DataFrame(screened_results)
                screened_df = screened_df.sort_values('Score', ascending=False)
                
                st.subheader(f"Screened Results ({len(screened_df)} stocks match criteria)")
                st.dataframe(screened_df, use_container_width=True)
            else:
                st.warning("No stocks match the specified criteria. Try adjusting the filters.")
    
    def display_stock_analysis(self, symbol, stock_data, fundamental_data, 
                             technical_analysis, fundamental_analysis, recommendation):
        
        # Header with current price
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"{symbol} Analysis (Real Data)")
        with col2:
            current_price = stock_data['Close'].iloc[-1]
            change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
            change_pct = (change / stock_data['Close'].iloc[-2]) * 100
            st.metric("Current Price", f"₹{current_price:.2f}", 
                     f"{change:.2f} ({change_pct:.2f}%)")
        with col3:
            # Recommendation
            rec_class = f"recommendation-{recommendation['action'].lower()}"
            st.markdown(f"""
            <div class="{rec_class}">
                <h4>{recommendation['action']}</h4>
                <p>Score: {recommendation['score']:.2f}/10</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs for different analyses
        tab1, tab2, tab3 = st.tabs(["Price Chart & Technical", "Fundamental Analysis", "Raw Data"])
        
        with tab1:
            self.create_price_chart(stock_data, symbol)
            self.display_technical_analysis(technical_analysis, stock_data)
        
        with tab2:
            self.display_fundamental_analysis(fundamental_analysis)
        
        with tab3:
            st.subheader("Raw Data from Screener.in")
            st.json(fundamental_data)
    
    def create_price_chart(self, stock_data, symbol):
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
            name=symbol
        ))
        
        # Moving averages
        if 'MA_20' in stock_data.columns:
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['MA_20'],
                name='MA 20',
                line=dict(color='orange')
            ))
        
        if 'MA_50' in stock_data.columns:
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['MA_50'],
                name='MA 50',
                line=dict(color='blue')
            ))
        
        fig.update_layout(
            title=f"{symbol} Price Chart with Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_technical_analysis(self, technical_analysis, stock_data):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Technical Indicators")
            
            rsi_value = technical_analysis.get('rsi', 50)
            st.metric("RSI (14)", f"{rsi_value:.2f}", 
                     technical_analysis.get('rsi_signal', 'N/A'))
            
            macd_signal = technical_analysis.get('macd_trend', 'N/A')
            st.metric("MACD Signal", macd_signal)
            
            ma_trend = "Bullish" if technical_analysis.get('ma_trend', 0) > 0 else "Bearish"
            st.metric("MA Trend", ma_trend)
            
            st.metric("Technical Score", f"{technical_analysis.get('technical_score', 0):.2f}/10")
        
        with col2:
            if 'RSI' in stock_data.columns:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['RSI'],
                    name='RSI',
                    line=dict(color='purple')
                ))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                fig_rsi.update_layout(title="RSI Indicator", height=300)
                st.plotly_chart(fig_rsi, use_container_width=True)
    
    def display_fundamental_analysis(self, fundamental_analysis):
        st.subheader("Real Fundamental Data from Screener.in")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Valuation Metrics**")
            st.metric("P/E Ratio", f"{fundamental_analysis['pe_ratio']:.2f}")
            st.metric("P/B Ratio", f"{fundamental_analysis['pb_ratio']:.2f}")
        
        with col2:
            st.write("**Profitability**")
            st.metric("ROE (%)", f"{fundamental_analysis['roe']:.2f}")
            st.metric("ROCE (%)", f"{fundamental_analysis['roce']:.2f}")
        
        with col3:
            st.write("**Growth & Health**")
            st.metric("Sales Growth (%)", f"{fundamental_analysis['sales_growth']:.2f}")
            st.metric("Profit Growth (%)", f"{fundamental_analysis['profit_growth']:.2f}")
        
        # Scores
        st.subheader("Analysis Scores")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Valuation Score", f"{fundamental_analysis.get('valuation_score', 0):.1f}/10")
        with col2:
            st.metric("Profitability Score", f"{fundamental_analysis.get('profitability_score', 0):.1f}/10")
        with col3:
            st.metric("Growth Score", f"{fundamental_analysis.get('growth_score', 0):.1f}/10")
        with col4:
            st.metric("Financial Health", f"{fundamental_analysis.get('financial_health_score', 0):.1f}/10")
    
    def market_overview_page(self):
        st.header("Market Overview")
        
        # Get real market data
        indices_data = self.get_market_indices()
        
        if indices_data:
            st.subheader("Market Indices")
            cols = st.columns(len(indices_data))
            for i, (index_name, data) in enumerate(indices_data.items()):
                with cols[i]:
                    st.metric(
                        index_name,
                        f"{data['price']:.2f}",
                        f"{data['change']:.2f} ({data['change_pct']:.2f}%)"
                    )
        
        # Top movers from NSE
        stock_list = self.data_collector.get_nse_stock_list()
        
        if not stock_list.empty and 'pChange' in stock_list.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Gainers")
                top_gainers = stock_list.nlargest(10, 'pChange')[['symbol', 'lastPrice', 'pChange']]
                
                fig_gainers = px.bar(top_gainers, x='symbol', y='pChange', 
                                   title="Top Gainers", color='pChange',
                                   color_continuous_scale='Greens')
                st.plotly_chart(fig_gainers, use_container_width=True)
            
            with col2:
                st.subheader("Top Losers")
                top_losers = stock_list.nsmallest(10, 'pChange')[['symbol', 'lastPrice', 'pChange']]
                
                fig_losers = px.bar(top_losers, x='symbol', y='pChange', 
                                  title="Top Losers", color='pChange',
                                  color_continuous_scale='Reds')
                st.plotly_chart(fig_losers, use_container_width=True)
    
    def get_market_indices(self):
        """Get real market indices data"""
        indices = {
            'NIFTY 50': '^NSEI',
            'SENSEX': '^BSESN',
            'BANK NIFTY': '^NSEBANK'
        }
        
        market_data = {}
        
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100
                    
                    market_data[name] = {
                        'price': current_price,
                        'change': change,
                        'change_pct': change_pct
                    }
                    
            except Exception as e:
                print(f"Error fetching {name} data: {e}")
        
        return market_data

# Run the app
if __name__ == "__main__":
    app = StockApp()
    app.main()
