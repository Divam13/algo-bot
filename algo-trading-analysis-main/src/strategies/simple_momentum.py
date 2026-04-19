"""
Simple Momentum Strategy - Guaranteed to generate trades
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from loguru import logger

from strategies.base_strategy import BaseStrategy


class SimpleMomentum(BaseStrategy):
    """
    Simple momentum crossover strategy using moving averages
    Guaranteed to generate trades for demo purposes
    """
    
    def __init__(
        self,
        name: str = "Simple Momentum",
        fast_period: int = 10,
        slow_period: int = 30,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.fast_period = fast_period
        self.slow_period = slow_period
        logger.info(f"📊 Simple Momentum Strategy: Fast={fast_period}, Slow={slow_period}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals using simple moving average crossover
        """
        df = data.copy()
        
        # Calculate moving averages
        df['sma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['sma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Initialize signal column
        df['signal'] = 0
        
        # Generate signals based on MA position
        # Hold long when fast > slow, flat otherwise
        for i in range(self.slow_period, len(df)):
            if not pd.isna(df['sma_fast'].iloc[i]) and not pd.isna(df['sma_slow'].iloc[i]):
                # Check for crossovers to generate entry/exit signals
                currently_above = df['sma_fast'].iloc[i] > df['sma_slow'].iloc[i]
                previously_above = df['sma_fast'].iloc[i-1] > df['sma_slow'].iloc[i-1]
                
                if currently_above and not previously_above:
                    # Golden cross - buy signal
                    df.loc[df.index[i], 'signal'] = 1
                elif not currently_above and previously_above:
                    # Death cross - sell signal
                    df.loc[df.index[i], 'signal'] = -1
        
        num_signals = (df['signal'] != 0).sum()
        logger.success(f"✅ Generated {num_signals} crossover signals")
        
        return df
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return {
            **super().get_parameters(),
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
        }
