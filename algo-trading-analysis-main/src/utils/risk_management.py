"""
Risk Management Module
Functions for managing trading risk
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class RiskManager:
    """Risk management utilities for trading strategies"""
    
    def __init__(self, max_position_size: float = 0.1, 
                 max_portfolio_risk: float = 0.02,
                 stop_loss_pct: float = 0.05,
                 take_profit_pct: float = 0.10):
        """
        Initialize risk manager
        
        Args:
            max_position_size: Maximum position size as fraction of portfolio (10%)
            max_portfolio_risk: Maximum risk per trade as fraction of portfolio (2%)
            stop_loss_pct: Stop loss percentage (5%)
            take_profit_pct: Take profit percentage (10%)
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
    
    def calculate_position_size(self, capital: float, entry_price: float,
                               stop_loss_price: Optional[float] = None) -> float:
        """
        Calculate position size based on risk parameters
        
        Args:
            capital: Available capital
            entry_price: Entry price for position
            stop_loss_price: Stop loss price (optional)
            
        Returns:
            Position size in units
        """
        # Calculate based on max position size
        max_position_value = capital * self.max_position_size
        position_size = max_position_value / entry_price
        
        # Adjust based on stop loss if provided
        if stop_loss_price is not None:
            risk_per_unit = abs(entry_price - stop_loss_price)
            max_risk = capital * self.max_portfolio_risk
            position_size_risk = max_risk / risk_per_unit
            position_size = min(position_size, position_size_risk)
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, 
                           direction: str = 'long') -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            direction: 'long' or 'short'
            
        Returns:
            Stop loss price
        """
        if direction == 'long':
            return entry_price * (1 - self.stop_loss_pct)
        else:  # short
            return entry_price * (1 + self.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float,
                             direction: str = 'long') -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            direction: 'long' or 'short'
            
        Returns:
            Take profit price
        """
        if direction == 'long':
            return entry_price * (1 + self.take_profit_pct)
        else:  # short
            return entry_price * (1 - self.take_profit_pct)
    
    def check_risk_limits(self, portfolio_value: float,
                         positions: Dict,
                         max_drawdown: float = -0.20) -> Dict:
        """
        Check if risk limits are breached
        
        Args:
            portfolio_value: Current portfolio value
            positions: Current positions
            max_drawdown: Maximum allowed drawdown
            
        Returns:
            Dictionary with risk status
        """
        total_position_value = sum(
            pos['size'] * pos['current_price'] 
            for pos in positions.values()
        )
        position_ratio = total_position_value / portfolio_value
        
        risk_status = {
            'position_ratio': position_ratio,
            'position_limit_breached': position_ratio > self.max_position_size,
            'max_drawdown_breached': False,  # Would need historical data to calculate
            'all_clear': position_ratio <= self.max_position_size
        }
        
        return risk_status
    
    def calculate_kelly_criterion(self, win_rate: float, 
                                  avg_win: float, 
                                  avg_loss: float) -> float:
        """
        Calculate Kelly Criterion for position sizing
        
        Args:
            win_rate: Probability of winning trade
            avg_win: Average win amount
            avg_loss: Average loss amount (positive number)
            
        Returns:
            Kelly percentage (fraction of capital to risk)
        """
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use half-Kelly for safety
        return max(0, kelly * 0.5)
