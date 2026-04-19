
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.strategies.bt_momentum import MomentumStrategy
from src.strategies.bt_mean_reversion import MeanReversionStrategy
from src.backtesting.bt_engine import BacktestEngine
from src.utils.data_loader import load_csv_data, load_sample_data
import glob
import pandas as pd

def run_sample_backtest():
    print("="*60)
    print("RUNNING BACKTRADER BACKTEST WITH SAMPLE DATA")
    print("="*60)
    
    # Load Data
    data = load_sample_data(days=365)
    
    # 1. Test Momentum Strategy
    print("\n--- Testing Momentum Strategy ---")
    engine_mom = BacktestEngine(initial_capital=100000)
    engine_mom.add_data(data, name="SAMPLE_MOM")
    engine_mom.add_strategy(MomentumStrategy, short_period=20, long_period=50)
    
    metrics_mom = engine_mom.run()
    print(f"Momentum Strategy Metrics:")
    print(f"  Total Return: {metrics_mom['total_return']:.2%}")
    print(f"  Sharpe Ratio: {metrics_mom['sharpe_ratio']:.4f}") if metrics_mom['sharpe_ratio'] is not None else print("  Sharpe Ratio: N/A")
    print(f"  Max Drawdown: {metrics_mom['max_drawdown']:.2f}%")
    
    # 2. Test Mean Reversion Strategy
    print("\n--- Testing Mean Reversion Strategy ---")
    engine_mr = BacktestEngine(initial_capital=100000)
    engine_mr.add_data(data, name="SAMPLE_MR")
    engine_mr.add_strategy(MeanReversionStrategy, period=20, devfactor=2.0)
    
    metrics_mr = engine_mr.run()
    print(f"Mean Reversion Strategy Metrics:")
    print(f"  Total Return: {metrics_mr['total_return']:.2%}")
    print(f"  Sharpe Ratio: {metrics_mr['sharpe_ratio']:.4f}") if metrics_mr['sharpe_ratio'] is not None else print("  Sharpe Ratio: N/A")
    print(f"  Max Drawdown: {metrics_mr['max_drawdown']:.2f}%")

def run_real_data_backtest():
    print("\n" + "="*60)
    print("RUNNING BACKTRADER BACKTEST WITH FINNIFTY DATA (PART 1)")
    print("="*60)
    
    # Find the data file
    data_path = "data/Equity_1min/FINNIFTY_part1.csv"
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return

    # Load Data using custom CSV loader or general pandas loader
    # The existing files handle 'date' and 'time' separate, need to parse
    try:
        df = pd.read_csv(data_path)
        # Parse DateTime
        # Format in CSV appears to be: date="04-08-21", time=10:00:00
        # Need to clean up the date column which has extra chars possibly due to excess quoting in CSV inspection earlier
        # "=""04-08-21""" -> we need to handle this.
        
        # Simple cleanup function for the weird date format seen in `view_file` output earlier
        # "=""04-08-21""" -> 04-08-21
        df['date'] = df['date'].astype(str).str.replace('="', '').str.replace('"', '')
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%d-%m-%y %H:%M:%S')
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)
        
        print(f"Loaded {len(df)} rows of data.")
        
        # Run Backtest
        engine = BacktestEngine(initial_capital=100000)
        engine.add_data(df, name="FINNIFTY")
        engine.add_strategy(MomentumStrategy, short_period=50, long_period=200) # Intraday params might need tuning
        
        metrics = engine.run()
        print(f"Real Data Momentum Strategy Metrics:")
        print(f"  Total Return: {metrics['total_return']:.2%}")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.4f}") if metrics['sharpe_ratio'] is not None else print("  Sharpe Ratio: N/A")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        
    except Exception as e:
        print(f"Error loading or processing real data: {e}")

if __name__ == "__main__":
    run_sample_backtest()
    run_real_data_backtest()
