"""
Regime-HMM Momentum Strategy
Uses Hidden Markov Model to detect market regimes and adapt momentum trading
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from hmmlearn import hmm
from loguru import logger

from strategies.base_strategy import BaseStrategy


class RegimeHMMMomentum(BaseStrategy):
    """
    Hidden Markov Model-based Regime-Adaptive Momentum Strategy
    
    Detects 3 market regimes:
    - State 0: Trending (strong momentum)
    - State 1: Ranging (mean-reverting)
    - State 2: Volatile (high uncertainty)
    
    Adapts position sizing and signal generation based on detected regime.
    """
    
    def __init__(
        self,
        lookback: int = 60,
        regime_confidence_threshold: float = 0.7,
        momentum_short: int = 20,
        momentum_long: int = 60,
        **kwargs
    ):
        """
        Initialize HMM Momentum strategy
        
        Args:
            lookback: Historical window for feature calculation
            regime_confidence_threshold: Minimum probability for regime confidence
            momentum_short: Short-term momentum period
            momentum_long: Long-term momentum period
        """
        super().__init__(name="Regime-HMM Momentum", **kwargs)
        
        self.lookback = lookback
        self.regime_confidence_threshold = regime_confidence_threshold
        self.momentum_short = momentum_short
        self.momentum_long = momentum_long
        
        # HMM model (3 states)
        self.hmm_model = None
        self._initialize_hmm()
    
    def _initialize_hmm(self):
        """Initialize HMM model with 3 states"""
        # Create Gaussian HMM with 3 states
        self.hmm_model = hmm.GaussianHMM(
            n_components=3,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        
        # Set initial transition matrix (tendsto stay in same regime)
        self.hmm_model.startprob_ = np.array([0.33, 0.33, 0.34])
        self.hmm_model.transmat_ = np.array([
            [0.90, 0.07, 0.03],  # Trending -> stay trending
            [0.08, 0.88, 0.04],  # Ranging -> stay ranging
            [0.10, 0.15, 0.75],  # Volatile -> stay volatile
        ])
    
    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Extract features for HMM
        
        Returns:
            Array of shape (n_samples, n_features) with:
            - Returns
            - Volatility
            - Autocorrelation
        """
        df = data.copy()
        
        # Returns
        df['returns'] = df['close'].pct_change()
        
        # Rolling volatility (20-period)
        df['volatility'] = df['returns'].rolling(20).std()
        
        # Autocorrelation (5-period)
        df['autocorr'] = df['returns'].rolling(10).apply(
            lambda x: x.autocorr(lag=1) if len(x) >= 2 else 0,
            raw=False
        )
        
        # Fill NaNs
        df = df.fillna(method='bfill').fillna(0)
        
        # Stack features
        features = np.column_stack([
            df['returns'].values,
            df['volatility'].values,
            df['autocorr'].values
        ])
        
        return features
    
    def _train_hmm(self, features: np.ndarray):
        """Train HMM on features"""
        try:
            self.hmm_model.fit(features)
            logger.debug(f"  HMM trained on {len(features)} samples")
        except Exception as e:
            logger.warning(f"  HMM training failed: {e}, using default parameters")
    
    def _detect_regime(self, features: np.ndarray) -> tuple:
        """
        Detect current market regime
        
        Returns:
            (regime_id, confidence)
        """
        try:
            # Get state probabilities for latest sample
            probs = self.hmm_model.predict_proba(features)
            latest_probs = probs[-1]
            
            regime = np.argmax(latest_probs)
            confidence = latest_probs[regime]
            
            return regime, confidence
        except Exception as e:
            logger.warning(f"  Regime detection failed: {e}")
            return 1, 0.5  # Default to ranging regime
    
    def _calculate_momentum_signal(self, data: pd.DataFrame, idx: int) -> float:
        """Calculate momentum score"""
        if idx < self.momentum_long:
            return 0
        
        current_price = data.iloc[idx]['close']
        
        # Short-term momentum (20 days)
        price_20 = data.iloc[idx - self.momentum_short]['close']
        roc_20 = (current_price / price_20 - 1) * 100
        
        # Long-term momentum (60 days)
        price_60 = data.iloc[idx - self.momentum_long]['close']
        roc_60 = (current_price / price_60 - 1) * 100
        
        # Weighted combination
        momentum_score = 0.6 * roc_20 + 0.4 * roc_60
        
        # Normalize to [-1, 1]
        normalized = np.tanh(momentum_score / 5)
        
        return normalized
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals with regime adaptation
        
        Returns:
            DataFrame with 'signal' column (1=buy, 0=hold, -1=sell)
        """
        df = data.copy()
        
        # Initialize signal column
        df['signal'] = 0
        df['regime'] = 1
        df['regime_confidence'] = 0.0
        df['momentum_score'] = 0.0
        df['position_size_multiplier'] = 1.0
        
        # Extract features for HMM
        features = self._extract_features(df)
        
        # Train HMM on historical data
        train_end = min(len(df), 500)
        self._train_hmm(features[:train_end])
        
        logger.info(f"  Generating signals for {len(df)} bars...")
        
        # Generate signals for each bar
        for i in range(self.lookback, len(df)):
            # Get features up to current point
            hist_features = features[:i+1]
            
            # Detect regime
            regime, confidence = self._detect_regime(hist_features)
            df.iloc[i, df.columns.get_loc('regime')] = regime
            df.iloc[i, df.columns.get_loc('regime_confidence')] = confidence
            
            # Calculate momentum
            momentum = self._calculate_momentum_signal(df, i)
            df.iloc[i, df.columns.get_loc('momentum_score')] = momentum
            
            # Regime-adaptive signal generation
            signal = 0
            position_mult = 1.0
            
            if confidence > self.regime_confidence_threshold:
                if regime == 0:  # TRENDING
                    # Aggressive momentum following
                    if momentum > 0.01:  # Virtually anything triggers a trade
                        signal = 1
                        position_mult = 1.0
                    elif momentum < -0.01:
                        signal = -1
                        position_mult = 1.0
                    
                elif regime == 1:  # RANGING
                    # Counter-trend
                    if momentum < -0.01:
                        signal = 1
                        position_mult = 0.8
                    elif momentum > 0.01:
                        signal = -1
                        position_mult = 0.8
                
                else:  # regime == 2: VOLATILE
                    # Trade ANY volatility
                    if momentum > 0.01:
                        signal = 1
                        position_mult = 0.5
                    elif momentum < -0.01:
                        signal = -1
                        position_mult = 0.5
            
            df.iloc[i, df.columns.get_loc('signal')] = signal
            df.iloc[i, df.columns.get_loc('position_size_multiplier')] = position_mult
        
        logger.success(f"  ✅ Generated {(df['signal'] != 0).sum()} trade signals")
        
        # Add regime statistics
        regime_counts = df['regime'].value_counts()
        logger.info(f"  Regime distribution: {regime_counts.to_dict()}")
        
        return df
