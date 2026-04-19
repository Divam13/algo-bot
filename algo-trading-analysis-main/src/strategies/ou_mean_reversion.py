"""
Ornstein-Uhlenbeck Mean Reversion Strategy
Models price as OU stochastic process for optimal mean reversion trading
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from loguru import logger

from strategies.base_strategy import BaseStrategy


class OUMeanReversion(BaseStrategy):
    """
    Ornstein-Uhlenbeck Mean Reversion Strategy
    
    Models price (or log-price) as an OU process:
        dX_t = θ(μ - X_t)dt + σdW_t
    
    Where:
    - θ = speed of mean reversion
    - μ = long-term mean
    - σ = volatility
    
    Trades based on z-score of current price vs equilibrium,
    but only when mean reversion is strong (high θ).
    """
    
    def __init__(
        self,
        window: int = 60,
        entry_z_score: float = 2.0,
        exit_z_score: float = 0.5,
        min_theta: float = 0.05,
        max_half_life: int = 20,
        use_log_price: bool = True,
        **kwargs
    ):
        """
        Initialize OU Mean Reversion strategy
        
        Args:
            window: Rolling window for OU parameter estimation
            entry_z_score: Z-score threshold for entry
            exit_z_score: Z-score threshold for exit
            min_theta: Minimum theta for trade(fast mean reversion required)
            max_half_life: Maximum half-life in bars
            use_log_price: Whether to use log(price) instead of price
        """
        super().__init__(name="OU Mean Reversion", **kwargs)
        
        self.window = window
        self.entry_z_score = entry_z_score
        self.exit_z_score = exit_z_score
        self.min_theta = min_theta
        self.max_half_life = max_half_life
        self.use_log_price = use_log_price
    
    def estimate_ou_parameters(self, prices: np.ndarray) -> Tuple[float, float, float]:
        """
        Estimate OU parameters using Maximum Likelihood Estimation
        
        Args:
            prices: Array of prices (or log-prices)
        
        Returns:
            (theta, mu, sigma)
        """
        n = len(prices)
        if n < 2:
            return 0.0, np.mean(prices), np.std(prices)
        
        dt = 1.0  # Unit time step
        
        # Regression: X_{t+1} = a + b*X_t + epsilon
        X = prices[:-1]
        Y = prices[1:]
        
        # Calculate regression coefficients
        X_mean = np.mean(X)
        Y_mean = np.mean(Y)
        
        numerator = np.sum((X - X_mean) * (Y - Y_mean))
        denominator = np.sum((X - X_mean)**2)
        
        if denominator > 0:
            b = numerator / denominator
        else:
            b = 0.9  # Default
        
        a = Y_mean - b * X_mean
        
        # Calculate residuals
        Y_pred = a + b * X
        residuals = Y - Y_pred
        sigma_epsilon = np.std(residuals) if len(residuals) > 0 else 1.0
        
        # Convert regression parameters to OU parameters
        if b > 0 and b < 1:
            theta = -np.log(b) / dt
            mu = a / (1 - b) if abs(1 - b) > 1e-6 else np.mean(prices)
            
            # Calculate sigma
            denom = (1 - b**2)
            if denom > 0:
                sigma = sigma_epsilon * np.sqrt(-2 * np.log(b) / denom)
            else:
                sigma = sigma_epsilon
        else:
            # Fallback if b is invalid
            theta = 0.01
            mu = np.mean(prices)
            sigma = np.std(prices)
        
        return theta, mu, sigma
    
    def calculate_half_life(self, theta: float) -> float:
        """Calculate half-life of mean reversion"""
        if theta > 0:
            return np.log(2) / theta
        return np.inf
    
    def calculate_z_score(
        self,
        current_price: float,
        mu: float,
        theta: float,
        sigma: float
    ) -> float:
        """
        Calculate z-score relative to equilibrium distribution
        
        The equilibrium variance of OU process is σ²/(2θ)
        """
        if theta > 0:
            equilibrium_std = sigma / np.sqrt(2 * theta)
        else:
            equilibrium_std = sigma
        
        if equilibrium_std > 0:
            z_score = (current_price - mu) / equilibrium_std
        else:
            z_score = 0
        
        return z_score
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on OU process analysis
        
        Returns:
            DataFrame with 'signal' column (1=buy, 0=hold, -1=sell)
        """
        df = data.copy()
        
        # Use log prices if specified
        if self.use_log_price:
            df['price_transform'] = np.log(df['close'])
        else:
            df['price_transform'] = df['close']
        
        # Initialize columns
        df['signal'] = 0
        df['theta'] = 0.0
        df['mu'] = 0.0
        df['sigma'] = 0.0
        df['half_life'] = np.inf
        df['z_score'] = 0.0
        df['stop_loss'] = 0.0
        
        logger.info(f"  Generating OU mean reversion signals for {len(df)} bars...")
        
        # Track current position
        in_position = False
        
        # Generate signals for each bar
        for i in range(self.window, len(df)):
            # Get historical window
            window_prices = df['price_transform'].iloc[i-self.window:i].values
            
            # Estimate OU parameters
            theta, mu, sigma = self.estimate_ou_parameters(window_prices)
            
            # Calculate derived metrics
            half_life = self.calculate_half_life(theta)
            current_price = df.iloc[i]['price_transform']
            z_score = self.calculate_z_score(current_price, mu, theta, sigma)
            
            # Store metrics
            df.iloc[i, df.columns.get_loc('theta')] = theta
            df.iloc[i, df.columns.get_loc('mu')] = np.exp(mu) if self.use_log_price else mu
            df.iloc[i, df.columns.get_loc('sigma')] = sigma
            df.iloc[i, df.columns.get_loc('half_life')] = half_life
            df.iloc[i, df.columns.get_loc('z_score')] = z_score
            
            # Trading logic
            signal = 0
            
            # Only trade if mean reversion is strong
            if theta > self.min_theta and half_life < self.max_half_life:
                if not in_position:
                    # Entry signals
                    if z_score < -self.entry_z_score:
                        # Price below mean - BUY (expect reversion up)
                        signal = 1
                        in_position = True
                        
                        # Set stop loss at 4 standard deviations
                        if self.use_log_price:
                            stop_price_log = mu - 4 * (sigma / np.sqrt(2 * theta))
                            stop_price = np.exp(stop_price_log)
                        else:
                            stop_dev = 4 * (sigma / np.sqrt(2 * theta))
                            stop_price = mu - stop_dev
                        df.iloc[i, df.columns.get_loc('stop_loss')] = stop_price
                    
                    elif z_score > self.entry_z_score:
                        # Price above mean - SHORT (expect reversion down)
                        # For now, we'll skip short signals in MVP
                        pass
                
                else:  # in_position
                    # Exit signal - mean achieved
                    if abs(z_score) < self.exit_z_score:
                        signal = -1
                        in_position = False
                    
                    # Also exit if regime changed (theta too low)
                    elif theta < self.min_theta:
                        signal = -1
                        in_position = False
                        logger.debug(f"  Exiting - mean reversion weakened (θ={theta:.4f})")
            
            else:
                # Mean reversion too weak - exit if in position
                if in_position:
                    signal = -1
                    in_position = False
            
            df.iloc[i, df.columns.get_loc('signal')] = signal
        
        # Convert mu back to price space for display
        if self.use_log_price:
            # mu is already converted above
            pass
        
        num_signals = (df['signal'] != 0).sum()
        logger.success(f"  ✅ Generated {num_signals} trade signals")
        
        # Statistics
        mean_theta = df[df['theta'] > 0]['theta'].mean()
        mean_half_life = df[df['half_life'] < 100]['half_life'].mean()
        logger.info(f"  Avg θ: {mean_theta:.4f}, Avg half-life: {mean_half_life:.1f} bars")
        
        return df
