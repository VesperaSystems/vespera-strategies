"""Push results to Vespera Mission Control (the hub).

Notebooks and runner.py use the same two calls:

    from vespera_strategies.reporting import post_backtest_run, post_signal

    post_backtest_run(df, summary, base_url=..., api_key=..., source="colab")
    post_signal(summary, base_url=..., api_key=...)

Auth is a shared API key sent as the `x-vespera-api-key` header
(set VESPERA_API_URL / VESPERA_API_KEY env vars to avoid passing them).
"""

import os

import pandas as pd
import requests

MAX_CURVE_POINTS = 250  # keep equity-curve payloads chart-sized


def _config(base_url, api_key):
    base_url = base_url or os.environ.get("VESPERA_API_URL")
    api_key = api_key or os.environ.get("VESPERA_API_KEY")
    if not base_url or not api_key:
        raise ValueError(
            "Set base_url/api_key arguments or VESPERA_API_URL / VESPERA_API_KEY env vars"
        )
    return base_url.rstrip("/"), api_key


def _downsample_curve(df, max_points=MAX_CURVE_POINTS):
    """Equity curves as [{date, strategy, buyHold}], thinned to ~max_points."""
    step = max(1, len(df) // max_points)
    sampled = df.iloc[::step]
    if df.index[-1] not in sampled.index:
        sampled = pd.concat([sampled, df.iloc[[-1]]])
    return [
        {
            "date": idx.date().isoformat(),
            "strategy": round(float(row["Cumulative_Strategy"]), 6),
            "buyHold": round(float(row["Cumulative_Market"]), 6),
        }
        for idx, row in sampled.iterrows()
    ]


def build_run_payload(df, summary, source="colab"):
    """Assemble the JSON body for POST /api/backtests from a run's outputs."""
    return {
        "strategy": summary["strategy"],
        "ticker": summary["ticker"],
        "params": summary["params"],
        "startDate": summary["start"],
        "endDate": summary["end"],
        "metrics": summary["metrics"],
        "latestSignal": summary["latest_signal"],
        "equityCurve": _downsample_curve(df),
        "source": source,
    }


def post_backtest_run(df, summary, base_url=None, api_key=None, source="colab", timeout=30):
    """POST a completed backtest to mission-control. Returns the parsed response."""
    base_url, api_key = _config(base_url, api_key)
    resp = requests.post(
        f"{base_url}/api/backtests",
        json=build_run_payload(df, summary, source=source),
        headers={"x-vespera-api-key": api_key},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def post_signal(summary, base_url=None, api_key=None, timeout=30):
    """POST the latest signal snapshot to mission-control (used by runner.py)."""
    base_url, api_key = _config(base_url, api_key)
    body = {
        "strategy": summary["strategy"],
        "ticker": summary["ticker"],
        "params": summary["params"],
        **summary["latest_signal"],
    }
    resp = requests.post(
        f"{base_url}/api/signals",
        json=body,
        headers={"x-vespera-api-key": api_key},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()
