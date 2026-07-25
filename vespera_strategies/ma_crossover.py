"""Moving Average Crossover strategy (Golden Cross / Death Cross).

Signal:  1 while the short SMA is above the long SMA, -1 while below, 0 otherwise.
Events:  a *golden cross* is the day Signal flips up to 1; a *death cross*
         is the day it flips down to -1.
"""

import pandas as pd

from vespera_strategies.data import fetch_stock_data
from vespera_strategies.metrics import summarize

GOLDEN_CROSS = "golden_cross"
DEATH_CROSS = "death_cross"


def apply_sma_crossover(df, short_window=50, long_window=200):
    """
    Adds short and long SMA columns, and generates a Signal column:
    1 = Buy (Golden Cross), -1 = Sell (Death Cross), 0 = Hold
    """
    df["SMA_Short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_Long"] = df["Close"].rolling(window=long_window).mean()

    df["Signal"] = 0
    df.loc[df["SMA_Short"] > df["SMA_Long"], "Signal"] = 1
    df.loc[df["SMA_Short"] < df["SMA_Long"], "Signal"] = -1

    return df


def compute_backtest(df):
    """
    Long-only, all-in/all-out backtest of the Signal column.
    Acts on the *next* bar after a signal (no lookahead).
    """
    df = df.copy()
    if "Signal" not in df.columns:
        raise KeyError("DataFrame must contain 'Signal' column from apply_sma_crossover")
    df["Position"] = df["Signal"].shift(1).fillna(0)  # act *after* the signal
    df["Market_Return"] = df["Close"].pct_change().fillna(0)
    df["Strategy_Return"] = df["Position"] * df["Market_Return"]
    df["Cumulative_Market"] = (1 + df["Market_Return"]).cumprod()
    df["Cumulative_Strategy"] = (1 + df["Strategy_Return"]).cumprod()
    return df


def detect_crossovers(df):
    """
    Return the crossover *events* as a DataFrame indexed by date with
    columns: event ('golden_cross' | 'death_cross'), close.
    """
    sig = df["Signal"]
    prev = sig.shift(1)
    golden = (sig == 1) & prev.notna() & (prev < 1)
    death = (sig == -1) & prev.notna() & (prev > -1)
    events = []
    for date in df.index[(golden | death)]:
        kind = GOLDEN_CROSS if bool(golden.loc[date]) else DEATH_CROSS
        events.append({"date": date, "event": kind, "close": float(df.loc[date, "Close"])})
    out = pd.DataFrame(events)
    if not out.empty:
        out = out.set_index("date")
    return out


def latest_signal(df):
    """
    Snapshot of where the strategy stands today. Returns a dict:
        state:       'long' | 'short' | 'flat' (current Signal)
        last_event:  'golden_cross' | 'death_cross' | None
        event_date:  ISO date of the last crossover (or None)
        close:       latest close price
    """
    state_map = {1: "long", -1: "short", 0: "flat"}
    events = detect_crossovers(df)
    last_event = None
    event_date = None
    if not events.empty:
        last = events.iloc[-1]
        last_event = last["event"]
        event_date = events.index[-1].date().isoformat()
    return {
        "state": state_map[int(df["Signal"].iloc[-1])],
        "last_event": last_event,
        "event_date": event_date,
        "close": float(df["Close"].iloc[-1]),
        "as_of": df.index[-1].date().isoformat(),
    }


def run_ma_crossover(ticker, start=None, end=None, short_window=50, long_window=200):
    """
    Convenience end-to-end run: fetch → signals → backtest → metrics.
    Returns (df, summary) where summary includes params and latest signal.
    Used by the notebooks and by runner.py so they always agree.
    """
    df = fetch_stock_data(ticker, start, end)
    df = apply_sma_crossover(df, short_window=short_window, long_window=long_window)
    df = compute_backtest(df)
    summary = {
        "strategy": "moving-average-crossover",
        "ticker": ticker,
        "params": {"short_window": short_window, "long_window": long_window},
        "start": df.index[0].date().isoformat(),
        "end": df.index[-1].date().isoformat(),
        "metrics": summarize(df),
        "latest_signal": latest_signal(df),
    }
    return df, summary
