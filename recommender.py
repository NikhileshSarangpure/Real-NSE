import numpy as np

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
            
            # Target price calculation
            target_price = self.calculate_target_price(fundamental_analysis, overall_score)
            
            return {
                'action': action,
                'score': overall_score,
                'confidence': confidence,
                'reasoning': reasoning,
                'risk_level': risk_level,
                'target_price': target_price,
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'growth_score': growth_score,
                'health_score': health_score,
                'components': {
                    'valuation': fundamental_analysis.get('valuation_score', 0),
                    'profitability': fundamental_analysis.get('profitability_score', 0),
                    'growth': growth_score,
                    'technical': technical_score
                }
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
    
    def calculate_target_price(self, fundamental, overall_score):
        """Calculate target price based on analysis"""
        try:
            # This is a simplified target price calculation
            # In practice, you'd use more sophisticated models like DCF
            
            base_multiplier = 1.0
            
            if overall_score > 7:
                base_multiplier = 1.15  # 15% upside
            elif overall_score > 6:
                base_multiplier = 1.08  # 8% upside
            elif overall_score > 5:
                base_multiplier = 1.0   # Fair value
            else:
                base_multiplier = 0.92  # 8% downside
            
            # Adjust based on growth prospects
            growth_factor = min(1.2, 1 + (fundamental.get('revenue_growth', 0) / 200))
            
            final_multiplier = base_multiplier * growth_factor
            
            return final_multiplier
            
        except Exception as e:
            return 1.0
    
    def generate_detailed_report(self, symbol, recommendation, technical, fundamental):
        """Generate a detailed analysis report"""
        report = f"""
        STOCK ANALYSIS REPORT - {symbol}
        
        RECOMMENDATION: {recommendation['action']} 
        Overall Score: {recommendation['score']:.2f}/10
        Confidence Level: {recommendation['confidence']}
        Risk Level: {recommendation['risk_level']}
        
        REASONING:
        {recommendation['reasoning']}
        
        TECHNICAL ANALYSIS:
        - RSI: {technical.get('rsi', 0):.2f} ({technical.get('rsi_signal', 'N/A')})
        - MACD: {technical.get('macd_trend', 'N/A')}
        - Moving Average Trend: {'Bullish' if technical.get('ma_trend', 0) > 0 else 'Bearish'}
        - Technical Score: {technical.get('technical_score', 0):.2f}/10
        
        FUNDAMENTAL ANALYSIS:
        - P/E Ratio: {fundamental.get('pe_ratio', 0):.2f}
        - ROE: {fundamental.get('roe', 0):.2f}%
        - Revenue Growth: {fundamental.get('revenue_growth', 0):.2f}%
        - Debt/Equity: {fundamental.get('debt_equity', 0):.2f}
        - Fundamental Score: {fundamental.get('fundamental_score', 0):.2f}/10
        
        TARGET PRICE MULTIPLIER: {recommendation.get('target_price', 1.0):.2f}x
        """
        
        return report