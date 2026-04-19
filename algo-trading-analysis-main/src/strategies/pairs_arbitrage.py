"""
Kalman Filter Pairs Arbitrage Strategy
Uses Kalman filtering to dynamically track hedge ratios for pairs trading
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from collections import deque
from loguru import logger

from strategies.base_strategy import BaseStrategy


class KalmanPairsArbitrage(BaseStrategy):
    """
    Kalman Filter-based Pairs Trading Strategy
    
    Uses a Kalman filter to estimate the time-varying hedge ratio β_t
    between two cointegrated assets, then trades the spread.
    
    State Space Model:
        β_t = β_{t-1} + w_t       (State equation)
        y_t = β_t × x_t + v_t     (Observation equation)
    """
    
    def __init__(
        self,
        pair_symbols: Tuple[str, str] = None,
        delta: float = 1e-4,
        vt: float = 1e-3,
        entry_z_score: float = 2.0,
        exit_z_score: float = 0.5,
        spread_window: int = 60,
        **kwargs
    ):
        """
        Initialize Kalman Pairs Arbitrage strategy
        
        Args:
            pair_symbols: Tuple of (symbol_a, symbol_b)
            delta: State transition variance
            vt: Observation variance
            entry_z_score: Z-score threshold for entry
            exit_z_score: Z-score threshold for exit
            spread_window: Window for spread statistics
        """
        super().__init__(name="Kalman Pairs Arbitrage", **kwargs)
        
        self.pair_symbols = pair_symbols
        self.delta = delta
        self.vt = vt
        self.entry_z_score = entry_z_score
        self.exit_z_score = exit_z_score
        self.spread_window = spread_window
        
        # Kalman filter state
        self.beta = 0.0
        self.P = 1.0
        self.spread_history = deque(maxlen=spread_window)
    
    def _kalman_update(self, price_a: float, price_b: float) -> Tuple[float, float]:
        """
        Kalman filter update step
        
        Args:
            price_a: Price of asset A
            price_b: Price of asset B
        
        Returns:
            (beta, spread)
        """
        # Prediction step
        R = self.P + self.delta
        
        # Observation
        y = price_a
        x = price_b
        
        # Innovation
        innovation = y - self.beta * x
        
        # Kalman gain
        S = x * R * x + self.vt
        K = R * x / S if S != 0 else 0
        
        # Update step
        self.beta = self.beta + K * innovation
        self.P = R - K * x * R
        
        # Calculate spread
        spread = price_a - self.beta * price_b
        
        return self.beta, spread
    
    def _calculate_z_score(self, spread: float) -> float:
        """Calculate z-score of current spread"""
        if len(self.spread_history) < 20:
            return 0.0
        
        spread_mean = np.mean(self.spread_history)
        spread_std = np.std(self.spread_history)
        
        if spread_std > 0:
            z_score = (spread - spread_mean) / spread_std
        else:
            z_score = 0.0
        
        return z_score
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals for pairs trading
        
        Note: This assumes data contains both symbols in the pair
        with columns like 'close_A' and 'close_B'
        
        Returns:
            DataFrame with 'signal' column
        """
        df = data.copy()
        
        # Check if we have pair data or need to merge
        if self.pair_symbols and len(self.pair_symbols) == 2:
            symbol_a, symbol_b = self.pair_symbols
            
            # Check if data has both symbols
            if 'symbol' in df.columns:
                # Data contains multiple symbols - need to pivot
                df_a = df[df['symbol'] == symbol_a][['close']].rename(columns={'close': 'price_a'})
                df_b = df[df['symbol'] == symbol_b][['close']].rename(columns={'close': 'price_b'})
                
                # Align indices
                df_merged = pd.merge(df_a, df_b, left_index=True, right_index=True, how='inner')
                df = df_merged
            else:
                # Assume columns are already named price_a, price_b or close_a, close_b
                if 'close_a' in df.columns and 'close_b' in df.columns:
                    df['price_a'] = df['close_a']
                    df['price_b'] = df['close_b']
                elif 'price_a' not in df.columns:
                    # Single asset - can't do pairs trading
                    logger.error("  ❌ Pairs trading requires data for both assets")
                    df['signal'] = 0
                    return df
            # Assume data already has price_a and price_b columns
            if 'price_a' not in df.columns or 'price_b' not in df.columns:
                if 'close' in df.columns:
                    logger.warning("⚠️ Single asset detected. Generatng synthetic pair for DEMO purposes.")
                    # Use 'close' as price_a
                    df['price_a'] = df['close']
                    # Create correlated asset price_b = price_a * (1 + 0.5% noise) + drift
                    np.random.seed(42)  # Fixed seed for reproducibility
                    noise = np.random.normal(0, 0.005, len(df))
                    drift = np.linspace(0, 0.02, len(df)) # Slight drift to force spread movement
                    df['price_b'] = df['price_a'] * (1 + noise + drift)
                else:
                    logger.error("  ❌ Data must have 'price_a' and 'price_b' columns")
                    df['signal'] = 0
                    return df
        
        # Initialize columns
        df['signal'] = 0
        df['beta'] = 0.0
        df['spread'] = 0.0
        df['z_score'] = 0.0
        
        # Reset Kalman filter
        self.beta = 0.0
        self.P = 1.0
        self.spread_history.clear()
        
        logger.info(f"  Generating Kalman pairs signals for {len(df)} bars...")
        
        # Track position state
        in_position = False
        
        # Generate signals
        for i in range(len(df)):
            price_a = df.iloc[i]['price_a']
            price_b = df.iloc[i]['price_b']
            
            # Kalman update
            beta, spread = self._kalman_update(price_a, price_b)
            self.spread_history.append(spread)
            
            # Calculate z-score
            z_score = self._calculate_z_score(spread)
            
            # Store metrics
            df.iloc[i, df.columns.get_loc('beta')] = beta
            df.iloc[i, df.columns.get_loc('spread')] = spread
            df.iloc[i, df.columns.get_loc('z_score')] = z_score
            
            # Trading logic
            signal = 0
            
            if len(self.spread_history) >= 20:  # Need enough history
                if not in_position:
                    # Entry signals
                    if z_score < -self.entry_z_score:
                        # Spread too low - LONG spread (buy A, sell B)
                        signal = 1
                        in_position = True
                    elif z_score > self.entry_z_score:
                        # Spread too high - SHORT spread (sell A, buy B)
                        # For MVP, skip short signals
                        pass
                else:
                    # Exit when spread mean-reverts
                    if abs(z_score) < self.exit_z_score:
                        signal = -1
                        in_position = False
            
            df.iloc[i, df.columns.get_loc('signal')] = signal
        
        num_signals = (df['signal'] != 0).sum()
        logger.success(f"  ✅ Generated {num_signals} trade signals")
        
        # Statistics
        avg_beta = df['beta'].mean()
        beta_std = df['beta'].std()
        logger.info(f"  Avg β: {avg_beta:.4f} ± {beta_std:.4f}")
        
        return df
    
    def calculate_position_size(
        self,
        signal: int,
        capital: float,
        price: float,
        stop_loss: Optional[float] = None
    ) -> float:
        """
        Override position sizing for pairs trading
        
        For pairs trading, we need to size both legs appropriately
        """
        if signal == 0:
            return 0
        
        # For pairs, allocate half the max position size to each leg
        max_position_value = capital * self.max_position_size * 0.5
        shares = max_position_value / price
        
        return int(shares)
