"""
Ensemble Strategy
Combines HMM Regime Detection with Momentum and Mean Reversion strategies
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from loguru import logger

from strategies.base_strategy import BaseStrategy
from strategies.regime_momentum import RegimeHMMMomentum
from strategies.ou_mean_reversion import OUMeanReversion
from strategies.simple_momentum import SimpleMomentum

class EnsembleStrategy(BaseStrategy):
    """
    Ensemble Strategy (Meta-Strategy)
    
    Logic:
    1. Uses HMM to detect market regime (Trending, Ranging, Volatile)
    2. Dispatches to specialized sub-strategies:
       - Trending -> Simple Momentum (Trend Following)
       - Ranging -> OU Mean Reversion (Statistical Arbitrage)
       - Volatile -> Cash (Risk Off)
    """
    
    def __init__(
        self,
        lookback: int = 500,
        **kwargs
    ):
        super().__init__(name="Ensemble (HMM + OU)", **kwargs)
        self.lookback = lookback
        
        # Initialize sub-strategies
        self.hmm_strategy = RegimeHMMMomentum(lookback=60, **kwargs)
        self.ou_strategy = OUMeanReversion(window=60, **kwargs)
        self.momentum_strategy = SimpleMomentum(fast_period=10, slow_period=30, **kwargs)
        
        logger.info("🧠 Initialized Ensemble Strategy with sub-strategies")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals by delegating to sub-strategies based on regime
        """
        df = data.copy()
        df['signal'] = 0
        df['regime'] = 1  # Default to ranging
        df['active_strategy'] = 'None'
        
        # 1. Detect Regimes (using HMM strategy logic)
        # We need to run the HMM strategy partially to get regimes
        # This is a bit inefficient (re-running full logic), but safe/clean
        logger.info("  🔍 Detecting regimes...")
        hmm_results = self.hmm_strategy.generate_signals(df)
        df['regime'] = hmm_results['regime']
        df['regime_confidence'] = hmm_results['regime_confidence']
        
        # 2. Run Sub-Strategies
        logger.info("  ⚡ Running sub-strategies...")
        ou_results = self.ou_strategy.generate_signals(df)
        mom_results = self.momentum_strategy.generate_signals(df)
        
        # 3. Ensemble Selection Logic
        logger.info("  🤖 Applying ensemble logic...")
        
        for i in range(len(df)):
            regime = df.iloc[i]['regime']
            confidence = df.iloc[i]['regime_confidence']
            
            # Default signal
            final_signal = 0
            strategy_name = 'Cash'
            
            if regime == 0:  # TRENDING
                # Use Momentum Strategy
                final_signal = mom_results.iloc[i]['signal']
                strategy_name = 'Momentum'
                
            elif regime == 1:  # RANGING
                # Use OU Mean Reversion
                final_signal = ou_results.iloc[i]['signal']
                strategy_name = 'MeanRev (OU)'
                
            elif regime == 2:  # VOLATILE
                # Cash / Low Risk
                # Only trade if extreme opportunity (optional)
                final_signal = 0
                strategy_name = 'Cash (Vol)'
            
            df.iloc[i, df.columns.get_loc('signal')] = final_signal
            df.iloc[i, df.columns.get_loc('active_strategy')] = strategy_name
            
        return df
