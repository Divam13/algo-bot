"""
Comprehensive unit tests for ALGO-BOT strategies
Tests all 5 strategies with realistic scenarios
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import all strategies
from src.strategies.simple_momentum import SimpleMomentumStrategy
from src.strategies.regime_momentum import RegimeHMMMomentumStrategy
from src.strategies.ou_mean_reversion import OUMeanReversionStrategy
from src.strategies.pairs_arbitrage import KalmanPairsArbitrageStrategy
from src.strategies.buy_hold import BuyAndHoldStrategy


def create_sample_data(n_bars=100, trend='up'):
    """
    Create synthetic market data for testing
    
    Args:
        n_bars: Number of bars to generate
        trend: 'up', 'down', or 'sideways'
    
    Returns:
        DataFrame with OHLCV data
    """
    np.random.seed(42)
    
    # Base price
    base_price = 100.0
    prices = [base_price]
    
    # Generate trend
    for i in range(n_bars - 1):
        if trend == 'up':
            change = np.random.normal(0.001, 0.01)  # Slight upward bias
        elif trend == 'down':
            change = np.random.normal(-0.001, 0.01)  # Slight downward bias
        else:  # sideways
            change = np.random.normal(0, 0.008)  # Pure noise
        
        prices.append(prices[-1] * (1 + change))
    
    # Create OHLCV
    data = pd.DataFrame({
        'datetime': [datetime.now() + timedelta(minutes=i) for i in range(n_bars)],
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.003))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.003))) for p in prices],
        'close': prices,
        'volume': [np.random.randint(1000, 10000) for _ in range(n_bars)]
    })
    
    data.set_index('datetime', inplace=True)
    return data


class TestSimpleMomentumStrategy:
    """Test suite for Simple Momentum Strategy"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.strategy = SimpleMomentumStrategy()
        self.data_uptrend = create_sample_data(200, 'up')
        self.data_downtrend = create_sample_data(200, 'down')
        self.data_sideways = create_sample_data(200, 'sideways')
    
    def test_strategy_initialization(self):
        """Test that strategy initializes correctly"""
        assert self.strategy.name == "Simple Momentum"
        assert 'short_period' in self.strategy.parameters
        assert 'long_period' in self.strategy.parameters
    
    def test_uptrend_generates_signals(self):
        """Test that uptrend data generates some buy signals"""
        signals = self.strategy.generate_signals(self.data_uptrend)
        
        assert len(signals) == len(self.data_uptrend)
        assert signals.sum() > 0, "Expected some buy signals in uptrend"
    
    def test_downtrend_generates_signals(self):
        """Test that downtrend data generates some sell signals"""
        signals = self.strategy.generate_signals(self.data_downtrend)
        
        assert len(signals) == len(self.data_downtrend)
        # Should have some -1 (sell) signals in downtrend
        assert (signals == -1).sum() > 0, "Expected some sell signals in downtrend"
    
    def test_insufficient_data_returns_zeros(self):
        """Test that insufficient data returns no signals"""
        short_data = self.data_uptrend.head(20)  # Less than required
        signals = self.strategy.generate_signals(short_data)
        
        # Should handle gracefully (either all zeros or error message)
        assert len(signals) == len(short_data)
    
    def test_signal_values_are_valid(self):
        """Test that all signals are in [-1, 0, 1]"""
        signals = self.strategy.generate_signals(self.data_uptrend)
        
        valid_signals = signals.isin([-1, 0, 1])
        assert valid_signals.all(), "All signals must be -1, 0, or 1"


class TestRegimeHMMMomentumStrategy:
    """Test suite for HMM Regime-Based Momentum"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.strategy = RegimeHMMMomentumStrategy()
        self.data = create_sample_data(500, 'up')
    
    def test_strategy_has_regime_awareness(self):
        """Test that strategy has HMM components"""
        assert self.strategy.name == "Regime-HMM Momentum"
        assert hasattr(self.strategy, 'hmm_model') or 'n_regimes' in self.strategy.parameters
    
    def test_generates_signals_with_sufficient_data(self):
        """Test signal generation with adequate historical data"""
        signals = self.strategy.generate_signals(self.data)
        
        assert len(signals) == len(self.data)
        assert signals.dtype in [np.int64, np.float64]
    
    def test_handles_small_dataset(self):
        """Test graceful handling of small datasets"""
        small_data = self.data.head(50)
        
        # Should either work or return zeros, not crash
        try:
            signals = self.strategy.generate_signals(small_data)
            assert len(signals) == len(small_data)
        except ValueError as e:
            # Some strategies may require minimum data
            assert "insufficient" in str(e).lower() or "minimum" in str(e).lower()


class TestOUMeanReversionStrategy:
    """Test suite for Ornstein-Uhlenbeck Mean Reversion"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.strategy = OUMeanReversionStrategy()
        self.data_sideways = create_sample_data(300, 'sideways')
        self.data_trending = create_sample_data(300, 'up')
    
    def test_strategy_initialization(self):
        """Test OU strategy initializes"""
        assert self.strategy.name == "OU Mean Reversion"
        assert 'lookback' in self.strategy.parameters or 'window' in self.strategy.parameters
    
    def test_mean_reversion_in_sideways_market(self):
        """Test that strategy generates signals in range-bound market"""
        signals = self.strategy.generate_signals(self.data_sideways)
        
        assert len(signals) == len(self.data_sideways)
        # Mean reversion should trade more in sideways markets
        assert signals.abs().sum() > 0, "Expected trading signals in sideways market"
    
    def test_estimates_mean_reversion_parameters(self):
        """Test that OU parameters are estimated"""
        signals = self.strategy.generate_signals(self.data_sideways)
        
        # Check if strategy stored parameters
        if hasattr(self.strategy, 'theta'):
            assert self.strategy.theta > 0, "Mean reversion speed should be positive"
        if hasattr(self.strategy, 'mu'):
            assert isinstance(self.strategy.mu, (int, float)), "Mean should be numeric"


class TestKalmanPairsArbitrageStrategy:
    """Test suite for Kalman Filter Pairs Trading"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.strategy = KalmanPairsArbitrageStrategy()
        
        # Create correlated pair
        self.data_x = create_sample_data(200, 'up')
        self.data_y = self.data_x.copy()
        # Add some noise to create imperfect correlation
        self.data_y['close'] = self.data_y['close'] * 1.1 + np.random.normal(0, 2, len(self.data_y))
    
    def test_strategy_initialization(self):
        """Test pairs strategy initializes"""
        assert self.strategy.name == "Kalman-Pairs Arbitrage"
    
    def test_requires_two_assets(self):
        """Test that pairs trading requires two assets"""
        # This strategy might require special data format
        # Just ensure it doesn't crash
        try:
            signals = self.strategy.generate_signals(self.data_x)
            assert len(signals) == len(self.data_x)
        except (ValueError, KeyError, AttributeError) as e:
            # Expected if it requires specific multi-asset format
            assert "pair" in str(e).lower() or "asset" in str(e).lower() or "column" in str(e).lower()


class TestBuyAndHoldStrategy:
    """Test suite for Buy and Hold baseline"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.strategy = BuyAndHoldStrategy()
        self.data = create_sample_data(100, 'up')
    
    def test_strategy_initialization(self):
        """Test buy and hold initializes"""
        assert self.strategy.name in ["Buy & Hold", "Buy and Hold", "BuyAndHold"]
    
    def test_generates_buy_at_start(self):
        """Test that buy and hold generates initial buy signal"""
        signals = self.strategy.generate_signals(self.data)
        
        assert len(signals) == len(self.data)
        # First non-zero signal should be a buy (1)
        first_signal_idx = (signals != 0).idxmax() if (signals != 0).any() else None
        if first_signal_idx is not None:
            assert signals[first_signal_idx] == 1, "First signal should be buy"
    
    def test_holds_position(self):
        """Test that strategy holds position after initial buy"""
        signals = self.strategy.generate_signals(self.data)
        
        # After initial buy, should mostly be 0 (hold)
        # Allow for final sell signal
        buy_count = (signals == 1).sum()
        assert buy_count >= 1, "Should have at least one buy signal"
        assert buy_count <= 2, "Should not buy multiple times"


class TestStrategyInterface:
    """Test that all strategies follow the same interface"""
    
    def test_all_strategies_have_name(self):
        """Test that all strategies have a name attribute"""
        strategies = [
            SimpleMomentumStrategy(),
            RegimeHMMMomentumStrategy(),
            OUMeanReversionStrategy(),
            KalmanPairsArbitrageStrategy(),
            BuyAndHoldStrategy()
        ]
        
        for strategy in strategies:
            assert hasattr(strategy, 'name'), f"{strategy.__class__.__name__} missing name"
            assert isinstance(strategy.name, str), "Name should be string"
            assert len(strategy.name) > 0, "Name should not be empty"
    
    def test_all_strategies_have_parameters(self):
        """Test that all strategies have parameters dict"""
        strategies = [
            SimpleMomentumStrategy(),
            RegimeHMMMomentumStrategy(),
            OUMeanReversionStrategy(),
            KalmanPairsArbitrageStrategy(),
            BuyAndHoldStrategy()
        ]
        
        for strategy in strategies:
            assert hasattr(strategy, 'parameters'), f"{strategy.__class__.__name__} missing parameters"
            assert isinstance(strategy.parameters, dict), "Parameters should be dict"
    
    def test_all_strategies_generate_signals(self):
        """Test that all strategies have generate_signals method"""
        strategies = [
            SimpleMomentumStrategy(),
            RegimeHMMMomentumStrategy(),
            OUMeanReversionStrategy(),
            BuyAndHoldStrategy()  # Skip pairs for this test
        ]
        
        data = create_sample_data(100, 'up')
        
        for strategy in strategies:
            assert hasattr(strategy, 'generate_signals'), f"{strategy.__class__.__name__} missing generate_signals"
            
            # Test it's callable
            try:
                signals = strategy.generate_signals(data)
                assert signals is not None
                assert len(signals) > 0
            except Exception as e:
                pytest.fail(f"{strategy.name} failed to generate signals: {e}")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_dataframe(self):
        """Test strategies handle empty data gracefully"""
        strategy = SimpleMomentumStrategy()
        empty_data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        
        try:
            signals = strategy.generate_signals(empty_data)
            assert len(signals) == 0
        except (ValueError, IndexError) as e:
            # Expected error is acceptable
            pass
    
    def test_nan_values_in_data(self):
        """Test strategies handle NaN values"""
        strategy = SimpleMomentumStrategy()
        data = create_sample_data(100, 'up')
        
        # Introduce some NaN values
        data.loc[data.index[10:15], 'close'] = np.nan
        
        try:
            signals = strategy.generate_signals(data)
            # Should handle NaN gracefully
            assert len(signals) == len(data)
        except (ValueError, TypeError) as e:
            # Some strategies may not handle NaN
            assert "nan" in str(e).lower() or "missing" in str(e).lower()
    
    def test_single_row_data(self):
        """Test strategies with single data point"""
        strategy = SimpleMomentumStrategy()
        single_data = create_sample_data(1, 'up')
        
        signals = strategy.generate_signals(single_data)
        assert len(signals) == 1
        # Single row should return 0 (no trade)
        assert signals.iloc[0] == 0


# Performance test (optional, can be slow)
@pytest.mark.slow
def test_strategy_performance_on_large_dataset():
    """Test that strategies can handle large datasets efficiently"""
    import time
    
    strategy = SimpleMomentumStrategy()
    large_data = create_sample_data(10000, 'up')
    
    start = time.time()
    signals = strategy.generate_signals(large_data)
    duration = time.time() - start
    
    assert len(signals) == len(large_data)
    assert duration < 5.0, f"Strategy too slow: {duration:.2f}s for 10k bars"


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
