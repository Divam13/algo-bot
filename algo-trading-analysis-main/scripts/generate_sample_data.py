"""
Generate sample OHLCV data for testing the frontend charts.
Creates CSV files in the data/ directory with realistic trading data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_ohlcv_data(
    symbol: str = "BTC-USD",
    start_date: str = "2024-01-01",
    days: int = 365,
    interval_minutes: int = 60,
    base_price: float = 45000.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Generate realistic OHLCV (Open, High, Low, Close, Volume) data.
    
    Args:
        symbol: Trading symbol
        start_date: Start date in YYYY-MM-DD format
        days: Number of days to generate
        interval_minutes: Interval in minutes (1, 5, 15, 60, 1440)
        base_price: Starting price
        volatility: Daily volatility (0.02 = 2%)
    
    Returns:
        DataFrame with OHLCV data
    """
    # Calculate number of data points
    intervals_per_day = (24 * 60) // interval_minutes
    total_intervals = days * intervals_per_day
    
    # Generate timestamps
    start = datetime.strptime(start_date, "%Y-%m-%d")
    timestamps = [start + timedelta(minutes=i * interval_minutes) for i in range(total_intervals)]
    
    # Generate price data using random walk
    np.random.seed(42)  # For reproducibility
    
    # Daily returns
    returns = np.random.normal(0, volatility / np.sqrt(intervals_per_day), total_intervals)
    
    # Add some trend
    trend = np.linspace(0, 0.3, total_intervals)  # 30% upward trend over period
    returns += trend / total_intervals
    
    # Calculate prices
    price_multipliers = np.exp(np.cumsum(returns))
    close_prices = base_price * price_multipliers
    
    # Generate OHLC from close prices
    data = []
    for i, (timestamp, close) in enumerate(zip(timestamps, close_prices)):
        # Add intrabar volatility
        intrabar_volatility = volatility * 0.5
        
        # Open is previous close (or base for first)
        open_price = close_prices[i-1] if i > 0 else base_price
        
        # High and Low with some randomness
        high = max(open_price, close) * (1 + np.random.uniform(0, intrabar_volatility))
        low = min(open_price, close) * (1 - np.random.uniform(0, intrabar_volatility))
        
        # Volume with some randomness (higher volume on bigger price moves)
        price_change = abs(close - open_price) / open_price
        base_volume = 1000000
        volume = int(base_volume * (1 + price_change * 10) * np.random.uniform(0.5, 1.5))
        
        data.append({
            'date': timestamp.strftime('%Y-%m-%d'),
            'time': timestamp.strftime('%H:%M:%S'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    return pd.DataFrame(data)

def generate_multiple_timeframes(symbol: str = "BTC-USD", output_dir: str = "data"):
    """Generate sample data for multiple timeframes."""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    timeframes = [
        # (interval_minutes, days, filename)
        (1, 7, f"{symbol}_1min_7days.csv"),       # 1-minute for 7 days
        (5, 30, f"{symbol}_5min_30days.csv"),     # 5-minute for 30 days
        (60, 365, f"{symbol}_1hour_1year.csv"),   # 1-hour for 1 year
        (1440, 730, f"{symbol}_1day_2years.csv"), # Daily for 2 years
    ]
    
    for interval, days, filename in timeframes:
        print(f"Generating {filename}...")
        df = generate_ohlcv_data(
            symbol=symbol,
            interval_minutes=interval,
            days=days
        )
        
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"  [OK] Created {filepath} with {len(df)} rows")

def generate_multiple_symbols():
    """Generate sample data for multiple trading symbols."""
    
    symbols = [
        ("BTC-USD", 45000),
        ("ETH-USD", 2500),
        ("AAPL", 180),
        ("GOOGL", 140),
    ]
    
    output_dir = "data/sample"
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol, base_price in symbols:
        print(f"\nGenerating data for {symbol}...")
        df = generate_ohlcv_data(
            symbol=symbol,
            base_price=base_price,
            days=365,
            interval_minutes=60
        )
        
        filepath = os.path.join(output_dir, f"{symbol}_1hour_1year.csv")
        df.to_csv(filepath, index=False)
        print(f"  [OK] Created {filepath} with {len(df)} rows")

if __name__ == "__main__":
    print("=" * 60)
    print("SAMPLE DATA GENERATOR FOR TRADING CHARTS")
    print("=" * 60)
    
    # Generate data for multiple timeframes
    generate_multiple_timeframes("BTC-USD", "data")
    
    # Generate data for multiple symbols
    print("\n" + "=" * 60)
    print("GENERATING MULTI-SYMBOL DATA")
    print("=" * 60)
    generate_multiple_symbols()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Sample data generation complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - data/BTC-USD_1min_7days.csv")
    print("  - data/BTC-USD_5min_30days.csv")
    print("  - data/BTC-USD_1hour_1year.csv")
    print("  - data/BTC-USD_1day_2years.csv")
    print("  - data/sample/BTC-USD_1hour_1year.csv")
    print("  - data/sample/ETH-USD_1hour_1year.csv")
    print("  - data/sample/AAPL_1hour_1year.csv")
    print("  - data/sample/GOOGL_1hour_1year.csv")
    print("\nYou can now run the frontend to visualize this data!")
