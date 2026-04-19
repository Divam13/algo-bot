"""
API routes for backtesting
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from loguru import logger
import pandas as pd
import uuid

from data.loader import DataLoader
from backtesting.engine import BacktestEngine
from api.strategies import create_strategy_instance

router = APIRouter(prefix="/api/backtest", tags=["Backtest"])

# Store backtest results (in production, use Redis or database)
backtest_results = {}


class BacktestRequest(BaseModel):
    """Request to run a backtest"""
    strategy_id: str
    parameters: Dict[str, Any] = {}
    data_source: str = "equity_1min"  # equity_1min, futures_daily, weekly
    symbol: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_bars: int = 5000  # Limit for performance
    initial_capital: float = 100000.0
    commission_rate: float = 0.001
    slippage_bps: float = 2.0


class BacktestStatus(BaseModel):
    """Backtest status"""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = 0.0
    message: str = ""


class BacktestResult(BaseModel):
    """Backtest result"""
    job_id: str
    strategy: str
    metrics: Dict[str, float]
    num_trades: int
    equity_curve: List[Dict[str, Any]]
    trades: List[Dict[str, Any]]


@router.post("/run", response_model=BacktestStatus)
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """
    Start a backtest job
    
    Returns immediately with a job_id. Use /status/{job_id} to check progress.
    """
    job_id = str(uuid.uuid4())
    
    # Initialize status
    backtest_results[job_id] = {
        "status": "pending",
        "progress": 0.0,
        "message": "Initializing backtest..."
    }
    
    # Run backtest in background
    background_tasks.add_task(
        _run_backtest_job,
        job_id=job_id,
        request=request
    )
    
    return BacktestStatus(
        job_id=job_id,
        status="pending",
        progress=0.0,
        message="Backtest queued"
    )


@router.get("/status/{job_id}", response_model=BacktestStatus)
async def get_backtest_status(job_id: str):
    """Get status of a backtest job"""
    if job_id not in backtest_results:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    result = backtest_results[job_id]
    return BacktestStatus(
        job_id=job_id,
        status=result["status"],
        progress=result.get("progress", 0.0),
        message=result.get("message", "")
    )


@router.get("/result/{job_id}", response_model=BacktestResult)
async def get_backtest_result(job_id: str):
    """Get results of a completed backtest"""
    if job_id not in backtest_results:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    result = backtest_results[job_id]
    
    if result["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Backtest not completed yet (status: {result['status']})"
        )
    
    return result["data"]


async def _run_backtest_job(job_id: str, request: BacktestRequest):
    """Background task to run backtest"""
    try:
        # Update status
        backtest_results[job_id]["status"] = "running"
        backtest_results[job_id]["message"] = "Loading data..."
        backtest_results[job_id]["progress"] = 0.1
        
        # Load data
        loader = DataLoader()
        
        if request.data_source == "equity_1min":
            data = loader.load_equity_1min()
        elif request.data_source == "futures_daily":
            data = loader.load_futures_daily()
        elif request.data_source == "weekly":
            data = loader.load_weekly()
        elif request.data_source == "options_minute":
            data = loader.load_options_minute()
        else:
            raise ValueError(f"Unknown data source: {request.data_source}")
        
        # Filter by symbol if needed
        if request.symbol and 'symbol' in data.columns:
            data = loader.get_symbol_data(
                data,
                symbol=request.symbol,
                start_date=request.start_date,
                end_date=request.end_date
            )
        
        # Limit bars for performance
        if len(data) > request.max_bars:
            logger.warning(f"Limiting data from {len(data)} to {request.max_bars} bars")
            data = data.tail(request.max_bars)
        
        # Set index
        date_col = 'datetime' if 'datetime' in data.columns else 'date'
        if date_col in data.columns:
            data = data.set_index(date_col)
        
        backtest_results[job_id]["message"] = f"Loaded {len(data)} bars"
        backtest_results[job_id]["progress"] = 0.3
        
        # Create strategy
        backtest_results[job_id]["message"] = "Initializing strategy..."
        strategy = create_strategy_instance(request.strategy_id, request.parameters)
        backtest_results[job_id]["progress"] = 0.4
        
        # Create backtest engine
        engine = BacktestEngine(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage_bps=request.slippage_bps
        )
        
        # Run backtest
        backtest_results[job_id]["message"] = "Running backtest..."
        backtest_results[job_id]["progress"] = 0.5
        
        results = engine.run(strategy, data, verbose=True)
        
        backtest_results[job_id]["progress"] = 0.9
        
        # Format results for API
        equity_curve = results['portfolio'][['datetime', 'value']].to_dict('records')
        trades = results['trades'].to_dict('records') if len(results['trades']) > 0 else []
        
        # Convert timestamps to strings
        for item in equity_curve:
            if 'datetime' in item:
                if hasattr(item['datetime'], 'timestamp'):
                     # Return unix timestamp (seconds)
                    item['datetime'] = item['datetime'].timestamp()
                elif isinstance(item['datetime'], str):
                     # Try to parse string if needed, or leave it
                     try:
                         dt = pd.to_datetime(item['datetime'])
                         item['datetime'] = dt.timestamp()
                     except:
                         pass
        
        for trade in trades:
            if 'datetime' in trade and hasattr(trade['datetime'], 'isoformat'):
                trade['datetime'] = trade['datetime'].isoformat()
        
        # Store final result
        backtest_results[job_id] = {
            "status": "completed",
            "progress": 1.0,
            "message": "Backtest completed successfully",
            "data": {
                "job_id": job_id,
                "strategy": results['strategy'],
                "metrics": results['metrics'],
                "num_trades": results['metrics']['num_trades'],
                "equity_curve": equity_curve,
                "trades": trades
            }
        }
        
        logger.success(f"✅ Backtest {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Backtest {job_id} failed: {e}")
        backtest_results[job_id] = {
            "status": "failed",
            "progress": 0.0,
            "message": f"Error: {str(e)}"
        }
