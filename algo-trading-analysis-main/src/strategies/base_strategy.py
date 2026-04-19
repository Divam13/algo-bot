"""
Base Strategy Abstract Class
All trading strategies must inherit from this class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from loguru import logger


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(
        self,
        name: str,
        initial_capital: float = 100000.0,
        max_position_size: float = 0.10,
        risk_per_trade: float = 0.02,
        **kwargs
    ):
        """
        Initialize base strategy
        
        Args:
            name: Strategy name
            initial_capital: Starting capital
            max_position_size: Maximum position size as fraction of capital
            risk_per_trade: Maximum risk per trade as fraction of capital
            **kwargs: Additional strategy-specific parameters
        """
        self.name = name
        self.initial_capital = initial_capital
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade
        self.parameters = kwargs
        
        logger.info(f"📊 Initialized strategy: {name}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from market data
        
        Args:
            data: Market data with OHLCV columns
        
        Returns:
            DataFrame with additional 'signal' column:
                1 = Buy/Long
                0 = Hold/Flat
                -1 = Sell/Short
        """
        pass
    
    def calculate_position_size(
        self,
        signal: int,
        capital: float,
        price: float,
        stop_loss: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk management rules
        
        Args:
            signal: Trading signal (1, 0, -1)
            capital: Available capital
            price: Current price
            stop_loss: Stop loss price (optional)
        
        Returns:
            Number of shares/contracts to trade
        """
        if signal == 0:
            return 0
        
        # Maximum position value based on position size limit
        max_position_value = capital * self.max_position_size
        
        # If stop loss provided, use risk-based sizing
        if stop_loss is not None and stop_loss > 0:
            risk_amount = capital * self.risk_per_trade
            price_risk = abs(price - stop_loss)
            
            if price_risk > 0:
                # Position size = Risk Amount / Price Risk
                shares = risk_amount / price_risk
                position_value = shares * price
                
                # Don't exceed max position size
                if position_value > max_position_value:
                    shares = max_position_value / price
            else:
                shares = max_position_value / price
        else:
            # Simple position sizing based on max position size
            shares = max_position_value / price
        
        # Ensure at least 1 share if we have enough capital
        # This fixes the issue where high-priced assets (like indices) prevent trading with small % allocation
        if int(shares) == 0 and capital >= price:
            shares = 1
        
        return int(shares)
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        direction: str,
        atr: Optional[float] = None,
        stop_pct: float = 0.02
    ) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            direction: 'long' or 'short'
            atr: Average True Range (optional, for ATR-based stops)
            stop_pct: Stop loss percentage (default 2%)
        
        Returns:
            Stop loss price
        """
        if atr is not None:
            # ATR-based stop loss (2x ATR)
            stop_distance = 2 * atr
        else:
            # Percentage-based stop loss
            stop_distance = entry_price * stop_pct
        
        if direction == 'long':
            return entry_price - stop_distance
        else:  # short
            return entry_price + stop_distance
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return {
            'name': self.name,
            'initial_capital': self.initial_capital,
            'max_position_size': self.max_position_size,
            'risk_per_trade': self.risk_per_trade,
            **self.parameters
        }
    
    def set_parameters(self, **kwargs):
        """Update strategy parameters"""
        self.parameters.update(kwargs)
        logger.info(f"Updated {self.name} parameters: {kwargs}")
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
