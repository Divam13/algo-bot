"""
Data Loading Utilities
Functions for loading and preprocessing market data
"""

import pandas as pd
import numpy as np
from typing import Optional, List
from datetime import datetime, timedelta


def load_sample_data(ticker: str = "SAMPLE", days: int = 365, 
                    start_price: float = 100) -> pd.DataFrame:
    """
    Generate sample market data for testing
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days of data
        start_price: Starting price
        
    Returns:
        DataFrame with OHLCV data
    """
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate random walk price data
    returns = np.random.normal(0.0005, 0.02, days)
    prices = start_price * (1 + returns).cumprod()
    
    # Generate OHLCV data
    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, days)),
        'high': prices * (1 + np.random.uniform(0, 0.02, days)),
        'low': prices * (1 + np.random.uniform(-0.02, 0, days)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    })
    
    data.set_index('date', inplace=True)
    return data


def load_csv_data(filepath: str, date_column: str = 'date') -> pd.DataFrame:
    """
    Load market data from CSV file
    
    Args:
        filepath: Path to CSV file
        date_column: Name of date column
        
    Returns:
        DataFrame with market data
    """
    data = pd.read_csv(filepath)
    data[date_column] = pd.to_datetime(data[date_column])
    data.set_index(date_column, inplace=True)
    return data


def preprocess_data(data: pd.DataFrame, 
                   fill_missing: bool = True,
                   remove_outliers: bool = False,
                   outlier_std: float = 3.0) -> pd.DataFrame:
    """
    Preprocess market data
    
    Args:
        data: Raw market data
        fill_missing: Whether to fill missing values
        remove_outliers: Whether to remove outliers
        outlier_std: Number of std deviations for outlier detection
        
    Returns:
        Preprocessed DataFrame
    """
    df = data.copy()
    
    # Fill missing values
    if fill_missing:
        df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Remove outliers
    if remove_outliers:
        for col in df.select_dtypes(include=[np.number]).columns:
            mean = df[col].mean()
            std = df[col].std()
            df = df[
                (df[col] >= mean - outlier_std * std) & 
                (df[col] <= mean + outlier_std * std)
            ]
    
    return df


def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate common technical indicators
    
    Args:
        data: Market data with OHLCV columns
        
    Returns:
        DataFrame with technical indicators
    """
    df = data.copy()
    
    # Simple Moving Averages
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['SMA_200'] = df['close'].rolling(window=200).mean()
    
    # Exponential Moving Average
    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    df['BB_std'] = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (2 * df['BB_std'])
    df['BB_lower'] = df['BB_middle'] - (2 * df['BB_std'])
    
    # RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    
    # Average True Range (ATR)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    return df
