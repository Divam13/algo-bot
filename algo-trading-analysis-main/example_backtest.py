"""
Example: Basic Strategy Backtest

This example demonstrates how to:
1. Load sample data
2. Initialize a trading strategy
3. Run a backtest
4. Analyze results
"""

from src.strategies.momentum_strategy import MomentumStrategy
from src.backtesting.engine import BacktestEngine
from src.utils.data_loader import load_sample_data


def main():
    print("=" * 60)
    print("Algo Trading Bot - Example Backtest")
    print("=" * 60)
    
    # 1. Load sample data
    print("\n1. Loading sample market data (365 days)...")
    data = load_sample_data(days=365)
    print(f"   Loaded {len(data)} days of data")
    print(f"   Date range: {data.index[0]} to {data.index[-1]}")
    print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    # 2. Initialize strategy
    print("\n2. Initializing Momentum Strategy...")
    strategy = MomentumStrategy(
        short_window=20,
        long_window=50,
        risk_per_trade=0.02
    )
    print(f"   Strategy: {strategy.name}")
    print(f"   Parameters: {strategy.parameters}")
    
    # 3. Run backtest
    print("\n3. Running backtest...")
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001
    )
    results = engine.run_backtest(strategy, data)
    print("   Backtest completed!")
    
    # 4. Display results
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    
    performance = results['performance']
    
    print(f"\nInitial Capital:  ${performance['initial_capital']:,.2f}")
    print(f"Final Value:      ${performance['final_value']:,.2f}")
    print(f"Total Return:     {performance['total_return']:.2%}")
    print(f"Number of Trades: {performance['num_trades']}")
    
    print(f"\n--- Risk Metrics ---")
    print(f"Sharpe Ratio:     {performance['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:     {performance['max_drawdown']:.2%}")
    print(f"Win Rate:         {performance['win_rate']:.2%}")
    
    # Show sample trades
    if len(results['trades']) > 0:
        print(f"\n--- Sample Trades (first 5) ---")
        print(results['trades'].head())
    
    print("\n" + "=" * 60)
    print("To visualize results, run: streamlit run ui/dashboard.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
