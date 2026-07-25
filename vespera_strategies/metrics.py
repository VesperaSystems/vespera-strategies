"""Performance metrics: Sharpe, drawdown, CAGR, and a full summary."""

import numpy as np

TRADING_DAYS = 252  # typical business days in a year


def sharpe_ratio(returns, rf=0.0, periods=TRADING_DAYS):
    """
    Annualized Sharpe Ratio of a periodic returns series.
    :param returns: Series of returns (e.g. daily)
    :param rf: Annual risk-free rate (decimal)
    :param periods: Number of periods per year (default 252)
    """
    excess = returns - rf / periods
    mu = excess.mean()
    sigma = excess.std(ddof=0)
    return 0.0 if sigma == 0 else float((mu / sigma) * np.sqrt(periods))


def max_drawdown(equity_curve):
    """
    Maximum drawdown of an equity curve, as a negative decimal
    (e.g. -0.35 means a 35% peak-to-trough loss).
    """
    roll_max = equity_curve.cummax()
    dd = equity_curve / roll_max - 1.0
    return float(dd.min())


def cagr(equity_curve, periods=TRADING_DAYS):
    """
    Compound annual growth rate implied by an equity curve
    that starts at 1.0.
    """
    n = len(equity_curve)
    if n < 2:
        return 0.0
    total = float(equity_curve.iloc[-1])
    if total <= 0:
        return -1.0
    years = n / periods
    return float(total ** (1 / years) - 1)


def summarize(df, rf=0.0):
    """
    Summary metrics for a backtested DataFrame (from compute_backtest):
    strategy vs buy-and-hold, side by side.

    Returns a dict like:
        {
          "strategy":  {"total_return": ..., "cagr": ..., "sharpe": ..., "max_drawdown": ...},
          "buy_hold":  {...},
        }
    """
    out = {}
    for label, ret_col, eq_col in (
        ("strategy", "Strategy_Return", "Cumulative_Strategy"),
        ("buy_hold", "Market_Return", "Cumulative_Market"),
    ):
        out[label] = {
            "total_return": float(df[eq_col].iloc[-1] - 1.0),
            "cagr": cagr(df[eq_col]),
            "sharpe": sharpe_ratio(df[ret_col], rf=rf),
            "max_drawdown": max_drawdown(df[eq_col]),
        }
    return out
