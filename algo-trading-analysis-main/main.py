"""
Algo Trading Bot - Main Entry Point
Integrated with Alpha Engine
"""
import sys
import os
from pathlib import Path

# Add src to path so imports work as expected (matching original structure)
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
sys.path.append(str(SRC_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

# Imports from src (now available directly)
from contextlib import asynccontextmanager

# Imports from src (now available directly)
from config import settings
from api import strategies, backtests

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Algo Trading Bot starting up...")
    logger.info(f"📊 Data directory: {settings.DATA_DIR}")
    logger.info(f"💰 Initial capital: ${settings.INITIAL_CAPITAL:,.2f}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Algo Trading Bot (Alpha Engine Pro)",
    description="High-Frequency Trading Platform | Backtesting | Live Execution",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategies.router)
app.include_router(backtests.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Algo Trading Bot",
        "system": "Pro"
    }

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )
