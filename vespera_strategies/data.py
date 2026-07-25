"""Market data helpers (Yahoo Finance via yfinance)."""

import pandas as pd
import yfinance as yf


def fetch_stock_data(ticker, start_date=None, end_date=None, auto_adjust=True):
    """
    Download daily OHLCV data for a single ticker.

    Returns a DataFrame with flat columns (Open, High, Low, Close, Volume)
    indexed by date. yfinance returns a MultiIndex (price, ticker) for
    single-ticker downloads in recent versions — we flatten it so strategy
    code can rely on plain 'Close' access.
    """
    df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=auto_adjust,
        progress=False,
    )
    if df is None or df.empty:
        raise ValueError(f"No data returned for ticker {ticker!r} ({start_date} → {end_date})")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    # yfinance can return a trailing NaN row for a not-yet-closed session
    df = df.dropna(subset=["Close"])
    if df.empty:
        raise ValueError(f"No usable rows for ticker {ticker!r} ({start_date} → {end_date})")
    return df
