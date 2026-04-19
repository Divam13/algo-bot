"""
API routes for strategies
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from strategies import RegimeHMMMomentum, OUMeanReversion, KalmanPairsArbitrage, SimpleMomentum, BuyHoldStrategy, EnsembleStrategy

router = APIRouter(prefix="/api/strategies", tags=["Strategies"])


class StrategyInfo(BaseModel):
    """Strategy information"""
    id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str


@router.get("/list", response_model=List[StrategyInfo])
async def list_strategies():
    """List all available strategies"""
    strategies = [
        {
            "id": "regime_hmm_momentum",
            "name": "Regime-HMM Momentum",
            "description": "Hidden Markov Model-based regime detection with adaptive momentum trading",
            "category": "Momentum",
            "parameters": {
                "lookback": {"type": "int", "default": 60, "min": 20, "max": 200},
                "regime_confidence_threshold": {"type": "float", "default": 0.7, "min": 0.5, "max": 0.95},
                "momentum_short": {"type": "int", "default": 20, "min": 5, "max": 50},
                "momentum_long": {"type": "int", "default": 60, "min": 20, "max": 200}
            }
        },
        {
            "id": "ou_mean_reversion",
            "name": "OU Mean Reversion",
            "description": "Ornstein-Uhlenbeck stochastic process modeling for mean reversion",
            "category": "Mean Reversion",
            "parameters": {
                "window": {"type": "int", "default": 60, "min": 20, "max": 200},
                "entry_z_score": {"type": "float", "default": 1.0, "min": 0.5, "max": 4.0},
                "exit_z_score": {"type": "float", "default": 0.5, "min": 0.1, "max": 2.0},
                "min_theta": {"type": "float", "default": 0.05, "min": 0.01, "max": 0.5},
                "max_half_life": {"type": "int", "default": 20, "min": 5, "max": 100}
            }
        },
        {
            "id": "kalman_pairs",
            "name": "Kalman Pairs Arbitrage",
            "description": "Kalman filter-based pairs trading with dynamic hedge ratio estimation",
            "category": "Arbitrage",
            "parameters": {
                "delta": {"type": "float", "default": 1e-4, "min": 1e-6, "max": 1e-2},
                "vt": {"type": "float", "default": 1e-3, "min": 1e-5, "max": 1e-1},
                "entry_z_score": {"type": "float", "default": 1.0, "min": 0.5, "max": 4.0},
                "exit_z_score": {"type": "float", "default": 0.5, "min": 0.1, "max": 2.0},
                "spread_window": {"type": "int", "default": 60, "min": 20, "max": 200}
            }
        },
        {
            "id": "simple_momentum",
            "name": "Simple Momentum",
            "description": "Simple moving average crossover strategy - guaranteed trades",
            "category": "Momentum",
            "parameters": {
                "fast_period": {"type": "int", "default": 10, "min": 5, "max": 50},
                "slow_period": {"type": "int", "default": 30, "min": 10, "max": 100}
            }
        },
        {
            "id": "buy_hold",
            "name": "Buy & Hold Demo",
            "description": "Simple buy and hold for demonstration - guaranteed results",
            "category": "Demo",
            "parameters": {}
        },
        {
            "id": "ensemble_strategy",
            "name": "Ensemble (HMM+OU)",
            "description": "Adaptive Meta-Strategy: Switches between Momentum (Trending), OU Mean Reversion (Ranging), and Cash (Volatile)",
            "category": "Advanced",
            "parameters": {
                "lookback": {"type": "int", "default": 500, "min": 200, "max": 2000}
            }
        }
    ]
    return strategies


@router.get("/{strategy_id}", response_model=StrategyInfo)
async def get_strategy(strategy_id: str):
    """Get details for a specific strategy"""
    strategies = await list_strategies()
    for strat in strategies:
        if strat["id"] == strategy_id:
            return strat
    raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")


def create_strategy_instance(strategy_id: str, parameters: Dict[str, Any]):
    """Create strategy instance from ID and parameters"""
    if strategy_id == "regime_hmm_momentum":
        return RegimeHMMMomentum(**parameters)
    elif strategy_id == "ou_mean_reversion":
        return OUMeanReversion(**parameters)
    elif strategy_id == "kalman_pairs":
        return KalmanPairsArbitrage(**parameters)
    elif strategy_id == "simple_momentum":
        return SimpleMomentum(**parameters)
    elif strategy_id == "buy_hold":
        return BuyHoldStrategy(**parameters)
    elif strategy_id == "ensemble_strategy":
        return EnsembleStrategy(**parameters)
    else:
        raise ValueError(f"Unknown strategy: {strategy_id}")
