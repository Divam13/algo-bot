"""
Mean Reversion Trading Strategy
Implements a Bollinger Bands-based mean reversion strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using Bollinger Bands"""
    
    def __init__(self, window: int = 20, num_std: float = 2.0, 
                 risk_per_trade: float = 0.02):
        """
        Initialize mean reversion strategy
        
        Args:
            window: Rolling window for calculating bands
            num_std: Number of standard deviations for bands
            risk_per_trade: Risk per trade as fraction of capital (default: 2%)
        """
        parameters = {
            'window': window,
            'num_std': num_std,
            'risk_per_trade': risk_per_trade
        }
        super().__init__(name="Mean Reversion Strategy", parameters=parameters)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on Bollinger Bands
        
        Args:
            data: DataFrame with 'close' price column
            
        Returns:
            DataFrame with 'signal' column (1: buy, -1: sell, 0: hold)
        """
        signals = data.copy()
        
        # Calculate Bollinger Bands
        signals['sma'] = signals['close'].rolling(
            window=self.parameters['window'], min_periods=1).mean()
        signals['std'] = signals['close'].rolling(
            window=self.parameters['window'], min_periods=1).std()
        signals['upper_band'] = signals['sma'] + (signals['std'] * self.parameters['num_std'])
        signals['lower_band'] = signals['sma'] - (signals['std'] * self.parameters['num_std'])
        
        # Generate signals
        signals['signal'] = 0
        # Buy when price touches lower band (oversold)
        signals.loc[signals['close'] <= signals['lower_band'], 'signal'] = 1
        # Sell when price touches upper band (overbought)
        signals.loc[signals['close'] >= signals['upper_band'], 'signal'] = -1
        
        # Signal changes
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
