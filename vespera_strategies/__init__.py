"""Vespera Systems quant lab — importable strategy library.

Core logic lives here so the same code powers:
- the learning notebooks (Colab/Jupyter)
- the plain scripts in each strategy folder
- the scheduled signal runner (runner.py)
"""

from vespera_strategies.data import fetch_stock_data
from vespera_strategies.ma_crossover import (
    apply_sma_crossover,
    compute_backtest,
    detect_crossovers,
    latest_signal,
    run_ma_crossover,
)
from vespera_strategies.metrics import cagr, max_drawdown, sharpe_ratio, summarize

__all__ = [
    "fetch_stock_data",
    "apply_sma_crossover",
    "compute_backtest",
    "detect_crossovers",
    "latest_signal",
    "run_ma_crossover",
    "sharpe_ratio",
    "max_drawdown",
    "cagr",
    "summarize",
]
