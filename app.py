import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import time

# Import custom modules
from data_collector import DataCollector
from analyzer import StockAnalyzer
from recommender import RecommendationEngine

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
        
        # Sample market data (in real app, fetch from NSE)
        with col1:
            st.metric("NIFTY 50", "19,122.15", "145.30 (0.77%)", delta_color="normal")
        with col2:
            st.metric("SENSEX", "64,112.65", "456.78 (0.72%)", delta_color="normal")
        with col3:
            st.metric("Bank NIFTY", "43,567.80", "-123.45 (-0.28%)", delta_color="inverse")
        with col4:
            st.metric("VIX", "13.25", "-0.45 (-3.29%)", delta_color="inverse")
        
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
        
        # Market heatmap
        self.create_market_heatmap()
    
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
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['MA_20'],
            name='MA 20',
            line=dict(color='orange')
        ))
        
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
            st.metric("RSI (14)", f"{technical_analysis['rsi']:.2f}", 
                     "Overbought" if technical_analysis['rsi'] > 70 else 
                     "Oversold" if technical_analysis['rsi'] < 30 else "Neutral")
            
            # MACD
            macd_signal = "Bullish" if technical_analysis['macd'] > technical_analysis['macd_signal'] else "Bearish"
            st.metric("MACD Signal", macd_signal)
            
            # Moving Average Trend
            ma_trend = "Bullish" if technical_analysis['ma_trend'] > 0 else "Bearish"
            st.metric("MA Trend", ma_trend)
        
        with col2:
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
        # Financial health score and metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Financial Strength")
            
            # Create a financial health score gauge
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
        
        # Screening filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pe_min = st.number_input("Min P/E Ratio", value=0.0, step=0.1)
            pe_max = st.number_input("Max P/E Ratio", value=50.0, step=0.1)
        
        with col2:
            roe_min = st.number_input("Min ROE (%)", value=15.0, step=1.0)
            debt_max = st.number_input("Max Debt/Equity", value=1.0, step=0.1)
        
        with col3:
            market_cap_min = st.selectbox("Min Market Cap", 
                                        ["Any", "Small Cap", "Mid Cap", "Large Cap"])
            sector = st.selectbox("Sector", 
                                ["All", "Banking", "IT", "Pharma", "Auto", "FMCG"])
        
        if st.button("Screen Stocks", type="primary"):
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
        
        # Add stock to portfolio
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            new_symbol = st.text_input("Stock Symbol")
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        with col3:
            avg_price = st.number_input("Avg Price", min_value=0.01, value=100.0)
        with col4:
            if st.button("Add to Portfolio"):
                st.success(f"Added {quantity} shares of {new_symbol}")
        
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
        st.subheader("Current Portfolio")
        st.dataframe(portfolio_df, use_container_width=True)
        
        # Portfolio metrics
        total_invested = sum(portfolio_df['Quantity'] * portfolio_df['Avg Price'])
        current_value = sum(portfolio_df['Quantity'] * portfolio_df['Current Price'])
        total_pnl = current_value - total_invested
        total_pnl_pct = (total_pnl / total_invested) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Invested", f"₹{total_invested:,.2f}")
        with col2:
            st.metric("Current Value", f"₹{current_value:,.2f}")
        with col3:
            st.metric("Total P&L", f"₹{total_pnl:,.2f}", f"{total_pnl_pct:.2f}%")
        with col4:
            st.metric("Portfolio Return", f"{total_pnl_pct:.2f}%")
    
    def market_overview_page(self):
        st.header("Market Overview")
        
        # Sector performance
        col1, col2 = st.columns(2)
        
        with col1:
            sectors_data = {
                "Sector": ["IT", "Banking", "Pharma", "Auto", "FMCG", "Metal"],
                "Change %": [2.45, 1.78, -0.89, 3.21, 0.67, -2.14]
            }
            
            fig_sectors = px.bar(sectors_data, x="Sector", y="Change %", 
                               title="Sector Performance Today",
                               color="Change %", 
                               color_continuous_scale="RdYlGn")
            st.plotly_chart(fig_sectors, use_container_width=True)
        
        with col2:
            # Market breadth
            breadth_data = {
                "Category": ["Advancing", "Declining", "Unchanged"],
                "Count": [1245, 987, 156]
            }
            
            fig_breadth = px.pie(breadth_data, values="Count", names="Category",
                               title="Market Breadth")
            st.plotly_chart(fig_breadth, use_container_width=True)
        
        # Market news (placeholder)
        st.subheader("Market News")
        news_items = [
            "RBI keeps repo rate unchanged at 6.50%",
            "SEBI introduces new regulations for F&O trading",
            "Q2 earnings season shows mixed results",
            "FII inflows continue for the third consecutive week"
        ]
        
        for news in news_items:
            st.write(f"• {news}")
    
    def create_market_heatmap(self):
        # Sample data for heatmap
        sectors = ['Banking', 'IT', 'Pharma', 'Auto', 'FMCG', 'Metal', 'Energy', 'Telecom']
        performance = [1.2, 2.1, -0.5, 1.8, 0.3, -1.2, 0.8, -0.3]
        
        fig = go.Figure(data=go.Heatmap(
            z=[performance],
            x=sectors,
            y=['Market Performance'],
            colorscale='RdYlGn',
            zmid=0
        ))
        
        fig.update_layout(
            title="Sector Performance Heatmap",
            height=200
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Run the app
if __name__ == "__main__":
    app = StockApp()
    app.main()
