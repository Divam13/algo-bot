"""
Unit tests for risk management
"""

import pytest
from src.utils.risk_management import RiskManager


class TestRiskManager:
    """Test cases for Risk Manager"""
    
    def test_initialization(self):
        """Test risk manager initialization"""
        rm = RiskManager(
            max_position_size=0.1,
            max_portfolio_risk=0.02,
            stop_loss_pct=0.05
        )
        assert rm.max_position_size == 0.1
        assert rm.max_portfolio_risk == 0.02
        assert rm.stop_loss_pct == 0.05
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        rm = RiskManager(max_position_size=0.1, max_portfolio_risk=0.02)
        
        position_size = rm.calculate_position_size(
            capital=100000,
            entry_price=100
        )
        
        assert position_size > 0
        assert position_size <= 100  # 10% of 100000 / 100
    
    def test_stop_loss_long(self):
        """Test stop loss calculation for long position"""
        rm = RiskManager(stop_loss_pct=0.05)
        
        stop_loss = rm.calculate_stop_loss(entry_price=100, direction='long')
        
        assert stop_loss == 95.0
    
    def test_stop_loss_short(self):
        """Test stop loss calculation for short position"""
        rm = RiskManager(stop_loss_pct=0.05)
        
        stop_loss = rm.calculate_stop_loss(entry_price=100, direction='short')
        
        assert stop_loss == 105.0
    
    def test_take_profit_long(self):
        """Test take profit calculation for long position"""
        rm = RiskManager(take_profit_pct=0.10)
        
        take_profit = rm.calculate_take_profit(entry_price=100, direction='long')
        
        assert abs(take_profit - 110.0) < 0.01  # Allow small floating point difference
    
    def test_kelly_criterion(self):
        """Test Kelly Criterion calculation"""
        rm = RiskManager()
        
        kelly = rm.calculate_kelly_criterion(
            win_rate=0.55,
            avg_win=100,
            avg_loss=50
        )
        
        assert kelly >= 0
        assert kelly <= 1


if __name__ == '__main__':
    pytest.main([__file__])
