"""
Unit tests for backtesting engine
"""

import pytest
import pandas as pd
import numpy as np
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import PerformanceMetrics
from src.strategies.momentum_strategy import MomentumStrategy
from src.utils.data_loader import load_sample_data


class TestBacktestEngine:
    """Test cases for Backtest Engine"""
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = BacktestEngine(initial_capital=100000, commission=0.001)
        assert engine.initial_capital == 100000
        assert engine.commission == 0.001
    
    def test_run_backtest(self):
        """Test backtest execution"""
        strategy = MomentumStrategy(short_window=10, long_window=20)
        data = load_sample_data(days=100)
        engine = BacktestEngine(initial_capital=100000)
        
        results = engine.run_backtest(strategy, data)
        
        assert 'strategy' in results
        assert 'results' in results
        assert 'trades' in results
        assert 'performance' in results
        assert results['strategy'] == "Momentum Strategy"
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        strategy = MomentumStrategy(short_window=10, long_window=20)
        data = load_sample_data(days=100)
        engine = BacktestEngine(initial_capital=100000)
        
        results = engine.run_backtest(strategy, data)
        performance = results['performance']
        
        assert 'total_return' in performance
        assert 'sharpe_ratio' in performance
        assert 'max_drawdown' in performance
        assert 'win_rate' in performance
        assert 'final_value' in performance


class TestPerformanceMetrics:
    """Test cases for Performance Metrics"""
    
    def test_calculate_returns(self):
        """Test returns calculation"""
        portfolio_values = pd.Series([100, 105, 103, 108, 110])
        returns = PerformanceMetrics.calculate_returns(portfolio_values)
        
        assert len(returns) == 4
        assert isinstance(returns, pd.Series)
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        returns = pd.Series([0.01, 0.02, -0.01, 0.015, 0.005])
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(returns)
        
        assert isinstance(sharpe, float)
        assert not np.isnan(sharpe)
    
    def test_max_drawdown(self):
        """Test maximum drawdown calculation"""
        portfolio_values = pd.Series([100, 110, 105, 95, 100, 108])
        dd_info = PerformanceMetrics.calculate_max_drawdown(portfolio_values)
        
        assert 'max_drawdown' in dd_info
        assert dd_info['max_drawdown'] <= 0
        assert 'drawdown_series' in dd_info


if __name__ == '__main__':
    pytest.main([__file__])
