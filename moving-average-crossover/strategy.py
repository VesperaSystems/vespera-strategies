"""Moving Average Crossover — thin wrapper around the shared package.

The core logic now lives in vespera_strategies/ma_crossover.py so the
notebook, this script, and the scheduled runner all share one implementation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vespera_strategies.ma_crossover import apply_sma_crossover  # noqa: E402,F401

if __name__ == "__main__":
    from vespera_strategies.ma_crossover import run_ma_crossover

    df, summary = run_ma_crossover("PLTR", start="2019-01-01")
    print(df[["Close", "SMA_Short", "SMA_Long", "Signal"]].tail(10))
    print()
    print("Latest signal:", summary["latest_signal"])
