"""
Performance Metrics Calculator
Calculates various performance and risk metrics for trading strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class PerformanceMetrics:
    """Calculate performance metrics for trading strategies"""
    
    @staticmethod
    def calculate_returns(portfolio_values: pd.Series) -> pd.Series:
        """Calculate period returns"""
        return portfolio_values.pct_change().dropna()
    
    @staticmethod
    def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
        """Calculate cumulative returns"""
        return (1 + returns).cumprod() - 1
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, 
                              periods: int = 252) -> float:
        """
        Calculate annualized Sharpe ratio
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods: Number of periods per year (252 for daily)
            
        Returns:
            Sharpe ratio
        """
        if returns.std() == 0:
            return 0
        
        excess_returns = returns - risk_free_rate / periods
        sharpe = np.sqrt(periods) * excess_returns.mean() / excess_returns.std()
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                               periods: int = 252) -> float:
        """
        Calculate annualized Sortino ratio
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods: Number of periods per year
            
        Returns:
            Sortino ratio
        """
        excess_returns = returns - risk_free_rate / periods
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        sortino = np.sqrt(periods) * excess_returns.mean() / downside_returns.std()
        return sortino
    
    @staticmethod
    def calculate_max_drawdown(portfolio_values: pd.Series) -> Dict:
        """
        Calculate maximum drawdown and related metrics
        
        Args:
            portfolio_values: Series of portfolio values
            
        Returns:
            Dictionary with max drawdown, duration, and recovery info
        """
        cumulative = portfolio_values / portfolio_values.iloc[0]
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        max_dd_idx = drawdown.idxmin()
        
        # Find drawdown period
        max_dd_end = max_dd_idx
        max_dd_start = drawdown[:max_dd_idx][drawdown[:max_dd_idx] == 0].index[-1] if any(drawdown[:max_dd_idx] == 0) else drawdown.index[0]
        
        return {
            'max_drawdown': max_dd,
            'max_drawdown_start': max_dd_start,
            'max_drawdown_end': max_dd_end,
            'drawdown_series': drawdown
        }
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, portfolio_values: pd.Series, 
                              periods: int = 252) -> float:
        """
        Calculate Calmar ratio (annual return / max drawdown)
        
        Args:
            returns: Series of returns
            portfolio_values: Series of portfolio values
            periods: Number of periods per year
            
        Returns:
            Calmar ratio
        """
        annual_return = returns.mean() * periods
        max_dd = abs(PerformanceMetrics.calculate_max_drawdown(portfolio_values)['max_drawdown'])
        
        if max_dd == 0:
            return 0
        
        return annual_return / max_dd
    
    @staticmethod
    def calculate_value_at_risk(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Series of returns
            confidence: Confidence level (default: 95%)
            
        Returns:
            VaR value
        """
        return returns.quantile(1 - confidence)
    
    @staticmethod
    def calculate_conditional_var(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR/Expected Shortfall)
        
        Args:
            returns: Series of returns
            confidence: Confidence level
            
        Returns:
            CVaR value
        """
        var = PerformanceMetrics.calculate_value_at_risk(returns, confidence)
        return returns[returns <= var].mean()
    
    @staticmethod
    def generate_performance_report(portfolio_values: pd.Series, 
                                   trades: Optional[pd.DataFrame] = None,
                                   initial_capital: float = 100000) -> Dict:
        """
        Generate comprehensive performance report
        
        Args:
            portfolio_values: Series of portfolio values
            trades: DataFrame of trades
            initial_capital: Initial capital
            
        Returns:
            Dictionary with all performance metrics
        """
        returns = PerformanceMetrics.calculate_returns(portfolio_values)
        
        metrics = {
            'total_return': (portfolio_values.iloc[-1] - initial_capital) / initial_capital,
            'annualized_return': returns.mean() * 252,
            'volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': PerformanceMetrics.calculate_sharpe_ratio(returns),
            'sortino_ratio': PerformanceMetrics.calculate_sortino_ratio(returns),
            'max_drawdown': PerformanceMetrics.calculate_max_drawdown(portfolio_values)['max_drawdown'],
            'calmar_ratio': PerformanceMetrics.calculate_calmar_ratio(returns, portfolio_values),
            'var_95': PerformanceMetrics.calculate_value_at_risk(returns),
            'cvar_95': PerformanceMetrics.calculate_conditional_var(returns)
        }
        
        if trades is not None and len(trades) > 0:
            metrics['num_trades'] = len(trades)
            # Add trade-specific metrics here if needed
        
        return metrics
