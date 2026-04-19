"""
Momentum Trading Strategy
Implements a simple momentum-based trading strategy using moving averages
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Momentum strategy using moving average crossover"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50, 
                 risk_per_trade: float = 0.02):
        """
        Initialize momentum strategy
        
        Args:
            short_window: Short-term moving average period
            long_window: Long-term moving average period
            risk_per_trade: Risk per trade as fraction of capital (default: 2%)
        """
        parameters = {
            'short_window': short_window,
            'long_window': long_window,
            'risk_per_trade': risk_per_trade
        }
        super().__init__(name="Momentum Strategy", parameters=parameters)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on moving average crossover
        
        Args:
            data: DataFrame with 'close' price column
            
        Returns:
            DataFrame with 'signal' column (1: buy, -1: sell, 0: hold)
        """
        signals = data.copy()
        
        # Calculate moving averages
        signals['short_ma'] = signals['close'].rolling(
            window=self.parameters['short_window'], min_periods=1).mean()
        signals['long_ma'] = signals['close'].rolling(
            window=self.parameters['long_window'], min_periods=1).mean()
        
        # Generate signals
        signals['signal'] = 0
        signals.loc[signals['short_ma'] > signals['long_ma'], 'signal'] = 1
        signals.loc[signals['short_ma'] < signals['long_ma'], 'signal'] = -1
        
        # Signal changes (entry/exit points)
        signals['positions'] = signals['signal'].diff()
        
        return signals
    
    def calculate_position_size(self, signal: int, capital: float, price: float) -> float:
        """
        Calculate position size based on fixed risk percentage
        
        Args:
            signal: Trading signal
            capital: Available capital
            price: Current asset price
            
        Returns:
            Position size (number of shares/units)
        """
        if signal == 0:
            return 0
        
        risk_amount = capital * self.parameters['risk_per_trade']
        position_size = risk_amount / price
        
        return position_size
