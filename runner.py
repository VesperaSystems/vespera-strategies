"""Scheduled signal runner — the executable form of the strategies.

For every active entry on the Mission Control watchlist:
  fetch prices → compute today's signal → POST it to /api/signals.
Mission Control decides whether the signal is new and sends notifications.

Environment:
    VESPERA_API_URL   e.g. https://vespera.systems
    VESPERA_API_KEY   shared key for the lab ingest endpoints

Usage:
    python runner.py                    # run everything on the watchlist
    python runner.py --ticker SPY      # one-off run for a single ticker
    python runner.py --dry-run          # compute but don't POST

Runs anywhere a container runs: Azure Container Apps Job, a Nebius VM
cron, or GitHub Actions (see .github/workflows/daily-signals.yml).
"""

import argparse
import os
import sys
from datetime import date, timedelta

import requests

from vespera_strategies.ma_crossover import run_ma_crossover
from vespera_strategies.reporting import post_signal

# The 200-day SMA needs ~200 trading days of history; 2 calendar years is a
# comfortable buffer (yfinance defaults to only 1 month when start is omitted).
LOOKBACK_DAYS = 730

STRATEGIES = {
    "moving-average-crossover": run_ma_crossover,
}


def fetch_watchlist(base_url, api_key):
    resp = requests.get(
        f"{base_url.rstrip('/')}/api/watchlist",
        headers={"x-vespera-api-key": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["entries"]


def run_entry(ticker, strategy, params, dry_run=False):
    runner = STRATEGIES.get(strategy)
    if runner is None:
        print(f"  ! unknown strategy {strategy!r}, skipping")
        return None

    kwargs = {}
    if params:
        if "short_window" in params:
            kwargs["short_window"] = int(params["short_window"])
        if "long_window" in params:
            kwargs["long_window"] = int(params["long_window"])

    start = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()
    _, summary = runner(ticker, start=start, **kwargs)
    sig = summary["latest_signal"]
    print(
        f"  {ticker}: {sig['state']} (last event: {sig['last_event']} on {sig['event_date']}, as of {sig['as_of']})"
    )
    if dry_run:
        return sig
    result = post_signal(summary)
    if result.get("isNewEvent"):
        print(f"  🔔 NEW {sig['last_event']} on {ticker} — notified: {result.get('notified')}")
    return sig


def main():
    parser = argparse.ArgumentParser(description="Run watchlist strategies and post signals.")
    parser.add_argument("--ticker", help="Run a single ticker instead of the watchlist")
    parser.add_argument("--strategy", default="moving-average-crossover")
    parser.add_argument("--dry-run", action="store_true", help="Compute signals but don't POST")
    args = parser.parse_args()

    base_url = os.environ.get("VESPERA_API_URL")
    api_key = os.environ.get("VESPERA_API_KEY")
    if not args.dry_run and (not base_url or not api_key):
        print("Set VESPERA_API_URL and VESPERA_API_KEY (or use --dry-run)", file=sys.stderr)
        return 1

    if args.ticker:
        entries = [{"ticker": args.ticker, "strategy": args.strategy, "params": None}]
    else:
        entries = fetch_watchlist(base_url, api_key)
        print(f"Watchlist: {len(entries)} active entries")

    failures = 0
    for entry in entries:
        print(f"→ {entry['ticker']} [{entry['strategy']}]")
        try:
            run_entry(entry["ticker"], entry["strategy"], entry.get("params"), dry_run=args.dry_run)
        except Exception as exc:  # keep going: one bad ticker shouldn't kill the run
            failures += 1
            print(f"  ! failed: {exc}", file=sys.stderr)

    print(f"Done — {len(entries) - failures}/{len(entries)} succeeded")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
