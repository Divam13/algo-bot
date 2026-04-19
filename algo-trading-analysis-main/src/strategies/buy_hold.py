"""
Ultra Simple Buy and Hold Strategy - For Demo
"""
import pandas as pd
from loguru import logger
from strategies.base_strategy import BaseStrategy


class BuyHoldStrategy(BaseStrategy):
    """
    Simple buy and hold - buys on first bar, sells on last bar
    For demonstration purposes
    """
    
    def __init__(self, name: str = "Buy & Hold Demo", **kwargs):
        super().__init__(name=name, **kwargs)
        logger.info(f"📊 Buy & Hold Strategy initialized")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate simple buy at start, sell at end"""
        df = data.copy()
        df['signal'] = 0
        
        # Buy on first valid bar (after some warmup)
        warmup = min(50, len(df) // 4)
        if len(df) > warmup + 10:
            df.iloc[warmup, df.columns.get_loc('signal')] = 1  # Buy
            df.iloc[-10, df.columns.get_loc('signal')] = -1   # Sell near end
        
        num_signals = (df['signal'] != 0).sum()
        logger.success(f"✅ Generated {num_signals} signals (buy + sell)")
        
        return df

    def calculate_position_size(self, signal: int, capital: float, price: float, stop_loss: float = None) -> int:
        """Always bet big - use 95% of capital"""
        if signal == 0:
            return 0
        
        # Use 95% of available capital
        allocation = capital * 0.95
        shares = int(allocation / price)
        
        # Ensure at least 1 share if credible capital exists
        if shares == 0 and capital > price:
            shares = 1
            
        return shares
