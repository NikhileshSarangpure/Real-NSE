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
import ta

# Page configuration
st.set_page_config(
    page_title="Stock Market Analysis Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

class DataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_data(self, symbol, period="6mo"):
        """Fetch stock price data from Yahoo Finance (NSE stocks)"""
        try:
            # Convert NSE symbol to Yahoo format
            yahoo_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            hist = stock.history(period=period)
            
            if hist.empty:
                return None
            
            # Calculate technical indicators
            hist['MA_20'] = hist['Close'].rolling(window=20).mean()
            hist['MA_50'] = hist['Close'].rolling(window=50).mean()
            hist['RSI'] = self.calculate_rsi(hist['Close'])
            
            return hist
            
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_fundamental_data(self, symbol):
        """Return sample fundamental data"""
        # Using sample data to avoid scraping issues
        sample_data = {
            'pe_ratio': 24.5,
            'pb_ratio': 3.2,
            'ev_ebitda': 12.8,
            'roe': 18.5,
            'roa': 8.7,
            'net_margin': 12.3,
            'revenue_growth': 15.2,
            'profit_growth': 22.1,
            'debt_equity': 0.45,
            'current_ratio': 2.1,
            'financial_health_score': 7.5
        }
        return sample_data
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

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
    
    def calculate_support_resistance(self, stock_data, lookback=20):
        """Calculate support and resistance levels"""
        try:
            recent_data = stock_data.tail(lookback)
            support = recent_data['Low'].min()
            resistance = recent_data['High'].max()
            return support, resistance
        except:
            return 0, 0
    
    # Scoring functions
    def get_rsi_signal(self, rsi):
        if rsi > 70:
            return "Overbought"
        elif rsi < 30:
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
        
        return max(0, min(10, score))  # Clamp between 0 and 10

class RecommendationEngine:
    def __init__(self):
        # Weights for different analysis components
        self.weights = {
            'technical': 0.25,
            'fundamental': 0.30,
            'growth': 0.25,
            'financial_health': 0.20
        }
    
    def get_recommendation(self, technical_analysis, fundamental_analysis):
        """Generate buy/sell/hold recommendation"""
        try:
            # Extract scores
            technical_score = technical_analysis.get('technical_score', 5)
            fundamental_score = fundamental_analysis.get('fundamental_score', 5)
            growth_score = fundamental_analysis.get('growth_score', 5)
            health_score = fundamental_analysis.get('financial_health_score', 5)
            
            # Calculate weighted overall score
            overall_score = (
                technical_score * self.weights['technical'] +
                fundamental_score * self.weights['fundamental'] +
                growth_score * self.weights['growth'] +
                health_score * self.weights['financial_health']
            )
            
            # Generate recommendation
            if overall_score >= 7:
                action = "BUY"
                confidence = "High"
                reasoning = self.get_buy_reasoning(technical_analysis, fundamental_analysis)
            elif overall_score >= 5.5:
                action = "HOLD"
                confidence = "Medium"
                reasoning = self.get_hold_reasoning(technical_analysis, fundamental_analysis)
            else:
                action = "SELL"
                confidence = "High"
                reasoning = self.get_sell_reasoning(technical_analysis, fundamental_analysis)
            
            # Risk assessment
            risk_level = self.assess_risk(technical_analysis, fundamental_analysis)
            
            return {
                'action': action,
                'score': overall_score,
                'confidence': confidence,
                'reasoning': reasoning,
                'risk_level': risk_level,
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'growth_score': growth_score,
                'health_score': health_score
            }
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return {
                'action': 'HOLD',
                'score': 5.0,
                'confidence': 'Low',
                'reasoning': 'Unable to analyze due to insufficient data',
                'risk_level': 'High'
            }
    
    def get_buy_reasoning(self, technical, fundamental):
        """Generate reasoning for BUY recommendation"""
        reasons = []
        
        if fundamental.get('roe', 0) > 15:
            reasons.append("Strong ROE indicates efficient management")
        
        if fundamental.get('revenue_growth', 0) > 15:
            reasons.append("Strong revenue growth trajectory")
        
        if technical.get('rsi', 50) < 70 and technical.get('ma_trend', 0) > 0:
            reasons.append("Technical indicators show bullish momentum")
        
        if fundamental.get('pe_ratio', 30) < 25:
            reasons.append("Attractive valuation metrics")
        
        if fundamental.get('debt_equity', 1) < 0.5:
            reasons.append("Healthy balance sheet with low debt")
        
        if not reasons:
            reasons.append("Overall positive indicators across multiple metrics")
        
        return " • ".join(reasons)
    
    def get_hold_reasoning(self, technical, fundamental):
        """Generate reasoning for HOLD recommendation"""
        reasons = ["Mixed signals across different analysis parameters"]
        
        if fundamental.get('fundamental_score', 5) > 6:
            reasons.append("Strong fundamentals but technical indicators are mixed")
        elif technical.get('technical_score', 5) > 6:
            reasons.append("Good technical setup but fundamental concerns exist")
        
        return " • ".join(reasons)
    
    def get_sell_reasoning(self, technical, fundamental):
        """Generate reasoning for SELL recommendation"""
        reasons = []
        
        if fundamental.get('pe_ratio', 0) > 35:
            reasons.append("Overvalued based on P/E ratio")
        
        if fundamental.get('debt_equity', 0) > 1.5:
            reasons.append("High debt levels pose financial risk")
        
        if technical.get('rsi', 50) > 70:
            reasons.append("Technical indicators show overbought conditions")
        
        if fundamental.get('revenue_growth', 0) < 0:
            reasons.append("Declining revenue growth")
        
        if fundamental.get('roe', 0) < 10:
            reasons.append("Poor return on equity")
        
        if not reasons:
            reasons.append("Multiple negative indicators suggest caution")
        
        return " • ".join(reasons)
    
    def assess_risk(self, technical, fundamental):
        """Assess investment risk level"""
        risk_factors = 0
        
        # Technical risk factors
        if technical.get('rsi', 50) > 80:
            risk_factors += 1
        
        # Fundamental risk factors
        if fundamental.get('debt_equity', 0) > 1:
            risk_factors += 1
        
        if fundamental.get('pe_ratio', 0) > 40:
            risk_factors += 1
        
        if fundamental.get('roe', 0) < 5:
            risk_factors += 1
        
        if risk_factors >= 3:
            return "High"
        elif risk_factors >= 1:
            return "Medium"
        else:
            return "Low"

class StockApp:
    def __init__(self):
        self.data_collector = DataCollector()
        self.analyzer = StockAnalyzer()
        self.recommender = RecommendationEngine()
        
    def main(self):
        st.title("📈 Real-Time Stock Analysis Platform")
        st.sidebar.title("Navigation")
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Dashboard", "Stock Analysis", "Stock Screener", "Portfolio", "Market Overview"]
        )
        
        if page == "Dashboard":
            self.dashboard_page()
        elif page == "Stock Analysis":
            self.stock_analysis_page()
        elif page == "Stock Screener":
            self.screener_page()
        elif page == "Portfolio":
            self.portfolio_page()
        elif page == "Market Overview":
            self.market_overview_page()
    
    def dashboard_page(self):
        st.header("Market Dashboard")
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("NIFTY 50", "19,122.15", "145.30 (0.77%)")
        with col2:
            st.metric("SENSEX", "64,112.65", "456.78 (0.72%)")
        with col3:
            st.metric("Bank NIFTY", "43,567.80", "-123.45 (-0.28%)")
        with col4:
            st.metric("VIX", "13.25", "-0.45 (-3.29%)")
        
        # Top gainers and losers
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Gainers")
            gainers_data = {
                "Stock": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
                "Price": [2456.78, 3234.56, 1567.89, 1654.32, 987.65],
                "Change %": [5.67, 4.23, 3.89, 3.45, 2.98]
            }
            st.dataframe(pd.DataFrame(gainers_data))
        
        with col2:
            st.subheader("Top Losers")
            losers_data = {
                "Stock": ["WIPRO", "LT", "ONGC", "COALINDIA", "NTPC"],
                "Price": [456.78, 2134.56, 187.89, 254.32, 187.65],
                "Change %": [-4.67, -3.23, -2.89, -2.45, -1.98]
            }
            st.dataframe(pd.DataFrame(losers_data))
    
    def stock_analysis_page(self):
        st.header("Individual Stock Analysis")
        
        # Stock selection
        col1, col2 = st.columns([2, 1])
        with col1:
            symbol = st.text_input("Enter Stock Symbol (NSE)", "RELIANCE").upper()
        with col2:
            analyze_btn = st.button("Analyze Stock", type="primary")
        
        if symbol and analyze_btn:
            with st.spinner("Fetching and analyzing data..."):
                # Fetch data
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
                    st.error("Unable to fetch data for the specified stock. Please check the symbol.")
    
    def display_stock_analysis(self, symbol, stock_data, fundamental_data, 
                             technical_analysis, fundamental_analysis, recommendation):
        
        # Header with current price
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"{symbol} Analysis")
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
        tab1, tab2, tab3, tab4 = st.tabs(["Price Chart", "Technical Analysis", 
                                          "Fundamental Analysis", "Financial Health"])
        
        with tab1:
            self.create_price_chart(stock_data, symbol)
        
        with tab2:
            self.display_technical_analysis(technical_analysis, stock_data)
        
        with tab3:
            self.display_fundamental_analysis(fundamental_analysis)
        
        with tab4:
            self.display_financial_health(fundamental_data)
    
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
            
            # RSI
            rsi_value = technical_analysis.get('rsi', 50)
            st.metric("RSI (14)", f"{rsi_value:.2f}", 
                     technical_analysis.get('rsi_signal', 'N/A'))
            
            # MACD
            macd_signal = technical_analysis.get('macd_trend', 'N/A')
            st.metric("MACD Signal", macd_signal)
            
            # Moving Average Trend
            ma_trend = "Bullish" if technical_analysis.get('ma_trend', 0) > 0 else "Bearish"
            st.metric("MA Trend", ma_trend)
            
            # Technical Score
            st.metric("Technical Score", f"{technical_analysis.get('technical_score', 0):.2f}/10")
        
        with col2:
            if 'RSI' in stock_data.columns:
                # RSI Chart
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Valuation Metrics")
            st.metric("P/E Ratio", f"{fundamental_analysis['pe_ratio']:.2f}")
            st.metric("P/B Ratio", f"{fundamental_analysis['pb_ratio']:.2f}")
            st.metric("EV/EBITDA", f"{fundamental_analysis['ev_ebitda']:.2f}")
        
        with col2:
            st.subheader("Profitability")
            st.metric("ROE (%)", f"{fundamental_analysis['roe']:.2f}")
            st.metric("ROA (%)", f"{fundamental_analysis['roa']:.2f}")
            st.metric("Net Margin (%)", f"{fundamental_analysis['net_margin']:.2f}")
        
        with col3:
            st.subheader("Growth Metrics")
            st.metric("Revenue Growth (%)", f"{fundamental_analysis['revenue_growth']:.2f}")
            st.metric("Profit Growth (%)", f"{fundamental_analysis['profit_growth']:.2f}")
            st.metric("Debt/Equity", f"{fundamental_analysis['debt_equity']:.2f}")
    
    def display_financial_health(self, fundamental_data):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Financial Strength")
            
            health_score = fundamental_data.get('financial_health_score', 7.5)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = health_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Financial Health Score"},
                delta = {'reference': 5},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 4], 'color': "lightgray"},
                        {'range': [4, 7], 'color': "gray"},
                        {'range': [7, 10], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.subheader("Key Financial Ratios")
            
            ratios_data = {
                "Metric": ["Current Ratio", "Quick Ratio", "Interest Coverage", 
                          "Asset Turnover", "Working Capital", "Cash Ratio"],
                "Value": [2.1, 1.8, 12.5, 1.2, "₹1,250 Cr", 0.45],
                "Benchmark": ["Good", "Good", "Excellent", "Average", "Strong", "Average"]
            }
            st.dataframe(pd.DataFrame(ratios_data))
    
    def screener_page(self):
        st.header("Stock Screener")
        st.write("Filter stocks based on your criteria")
        
        # Sample screened results
        screened_data = {
            "Symbol": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"],
            "Price": [2456.78, 3234.56, 1654.32, 1567.89, 987.65],
            "P/E": [24.5, 28.3, 18.7, 22.1, 16.8],
            "ROE": [18.5, 45.2, 17.8, 24.5, 16.9],
            "Debt/Equity": [0.45, 0.12, 0.78, 0.15, 0.89],
            "Recommendation": ["BUY", "HOLD", "BUY", "BUY", "HOLD"]
        }
        
        df_screened = pd.DataFrame(screened_data)
        st.dataframe(df_screened, use_container_width=True)
    
    def portfolio_page(self):
        st.header("Portfolio Tracking")
        st.write("Track your investment portfolio")
        
        # Portfolio summary
        portfolio_data = {
            "Symbol": ["RELIANCE", "TCS", "INFY"],
            "Quantity": [10, 5, 15],
            "Avg Price": [2200.00, 3100.00, 1450.00],
            "Current Price": [2456.78, 3234.56, 1567.89],
            "P&L": [2567.8, 672.8, 1768.35],
            "P&L %": [11.67, 4.34, 8.13]
        }
        
        portfolio_df = pd.DataFrame(portfolio_data)
        st.dataframe(portfolio_df, use_container_width=True)
    
    def market_overview_page(self):
        st.header("Market Overview")
        st.write("Overview of market performance")
        
        # Sector performance
        sectors_data = {
            "Sector": ["IT", "Banking", "Pharma", "Auto", "FMCG", "Metal"],
            "Change %": [2.45, 1.78, -0.89, 3.21, 0.67, -2.14]
        }
        
        fig_sectors = px.bar(sectors_data, x="Sector", y="Change %", 
                           title="Sector Performance Today",
                           color="Change %", 
                           color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_sectors, use_container_width=True)

# Run the app
if __name__ == "__main__":
    app = StockApp()
    app.main()
