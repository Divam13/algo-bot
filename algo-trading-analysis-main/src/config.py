"""
Configuration settings for Alpha Engine backend
"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    
    # C++ Engine
    CPP_ENGINE_ENABLED: bool = True
    CPP_ENGINE_HOST: str = "localhost"
    CPP_ENGINE_PORT: int = 50051
    
    # Backtesting defaults
    INITIAL_CAPITAL: float = 100000.0
    COMMISSION_RATE: float = 0.001  # 0.1%
    SLIPPAGE_BPS: float = 2.0  # 2 basis points
    
    # Strategy defaults
    MAX_POSITION_SIZE: float = 0.10  # 10% of capital per position
    MAX_RISK_PER_TRADE: float = 0.02  # 2% risk per trade
    
    # Data settings
    DEFAULT_SYMBOL: str = "NIFTY50"
    DEFAULT_TIMEFRAME: str = "1min"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
