"""Backtest CLI for the Moving Average Crossover strategy.

Core logic (signals, backtest math, metrics) lives in the shared
vespera_strategies package; this script adds plotting and a CLI.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # for static 3D
import plotly.graph_objs as go
import plotly.io as pio

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vespera_strategies.data import fetch_stock_data  # noqa: E402
from vespera_strategies.ma_crossover import apply_sma_crossover, compute_backtest  # noqa: E402
from vespera_strategies.metrics import summarize  # noqa: E402


class Plotter:
    """
    Wrapper that can render static Matplotlib plots or interactive Plotly plots.
    Use mode='static' for Matplotlib, mode='interactive' for Plotly.
    """

    def __init__(self, mode='static'):
        assert mode in ('static', 'interactive')
        self.mode = mode

    def plot_time_series(self, df, cols, title=None, ticker=None):
        title = title or 'Time Series'
        if self.mode == 'interactive':
            fig = go.Figure()
            for c in cols:
                if c not in df.columns:
                    continue
                fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c, mode='lines'))
            fig.update_layout(title=title if not ticker else f"{title} – {ticker}", xaxis_title='Date')
            pio.show(fig)
        else:
            plt.figure(figsize=(16, 8))
            for c in cols:
                if c not in df.columns:
                    continue
                plt.plot(df.index, df[c], label=c)
            plt.title(title if not ticker else f"{title} – {ticker}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    def plot_2d_scatter(self, df, x_col, y_col, color_col=None, title=None, ticker=None):
        title = title or '2D Scatter'
        if x_col not in df.columns or y_col not in df.columns:
            raise KeyError("x_col and y_col must exist in DataFrame")
        if self.mode == 'interactive':
            marker = dict(color=df[color_col] if color_col in df.columns else None, showscale=True) if color_col else {}
            fig = go.Figure(data=go.Scatter(
                x=df[x_col], y=df[y_col], mode='markers', marker=marker, text=df.index.astype(str)
            ))
            fig.update_layout(title=title if not ticker else f"{title} – {ticker}", xaxis_title=x_col, yaxis_title=y_col)
            pio.show(fig)
        else:
            plt.figure(figsize=(12, 8))
            sc = plt.scatter(df[x_col], df[y_col], c=(df[color_col] if color_col in df.columns else 'C0'), cmap='viridis', alpha=0.8)
            if color_col and color_col in df.columns:
                plt.colorbar(sc, label=color_col)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(title if not ticker else f"{title} – {ticker}")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    def plot_3d(self, df, x_col, y_col, z_col, title=None, ticker=None):
        title = title or '3D Chart'
        for c in (x_col, y_col, z_col):
            if c not in df.columns and c != 'index':
                raise KeyError(f"{c} must exist in DataFrame (or use 'index' for x axis)")
        # prepare x axis values
        if x_col == 'index':
            x_vals = df.index
        else:
            x_vals = df[x_col]

        if self.mode == 'interactive':
            fig = go.Figure(data=[go.Scatter3d(
                x=x_vals,
                y=df[y_col],
                z=df[z_col],
                mode='lines+markers',
                marker=dict(size=3, color=df[z_col], colorscale='Viridis', showscale=True)
            )])
            fig.update_layout(scene=dict(xaxis_title=x_col, yaxis_title=y_col, zaxis_title=z_col),
                              title=title if not ticker else f"{title} – {ticker}")
            pio.show(fig)
        else:
            # static Matplotlib 3D
            fig = plt.figure(figsize=(14, 9))
            ax = fig.add_subplot(111, projection='3d')
            if isinstance(x_vals, pd.DatetimeIndex):
                x_num = mdates.date2num(x_vals.to_pydatetime())
                ax.plot(x_num, df[y_col].values, df[z_col].values, lw=1)
                ax.set_xticks(x_num[:: max(1, len(x_num)//8)])
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.gcf().autofmt_xdate()
            else:
                ax.plot(x_vals, df[y_col].values, df[z_col].values, lw=1)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_zlabel(z_col)
            plt.title(title if not ticker else f"{title} – {ticker}")
            plt.tight_layout()
            plt.show()


def print_metrics(df, ticker):
    """Strategy vs buy-and-hold summary table."""
    stats = summarize(df)
    table = pd.DataFrame(stats).rename(
        index={
            "total_return": "Total return",
            "cagr": "CAGR",
            "sharpe": "Sharpe (ann.)",
            "max_drawdown": "Max drawdown",
        },
        columns={"strategy": "Strategy", "buy_hold": "Buy & Hold"},
    )
    formatted = table.copy().astype(object)
    for row in formatted.index:
        fmt = "{:.2f}" if row == "Sharpe (ann.)" else "{:.2%}"
        formatted.loc[row] = [fmt.format(v) for v in table.loc[row]]
    print(f"\nPerformance — {ticker}")
    print(formatted.to_string())
    return stats


def main():
    parser = argparse.ArgumentParser(description="Backtest and plot (static/interactive).")
    parser.add_argument("--ticker", default="PLTR")
    parser.add_argument("--start", default="2015-01-01")
    parser.add_argument("--end", default="2024-01-01")
    parser.add_argument("--short", type=int, default=50, help="Short SMA window")
    parser.add_argument("--long", type=int, default=200, help="Long SMA window")
    parser.add_argument("--interactive", action="store_true", help="Use Plotly interactive plotting")
    parser.add_argument("--charts", choices=['1d', '2d', '3d', 'all', 'none'], default='all')
    args = parser.parse_args()

    df = fetch_stock_data(args.ticker, args.start, args.end)
    df = apply_sma_crossover(df, short_window=args.short, long_window=args.long)
    df = compute_backtest(df)

    mode = 'interactive' if args.interactive else 'static'
    plotter = Plotter(mode=mode)

    if args.charts in ('1d', 'all'):
        plotter.plot_time_series(df, ['Cumulative_Market', 'Cumulative_Strategy'], title='Backtest vs Market', ticker=args.ticker)
    if args.charts in ('2d', 'all') and 'Volume' in df.columns:
        plotter.plot_2d_scatter(df, 'Close', 'Volume', color_col='Market_Return' if 'Market_Return' in df.columns else None, title='Price vs Volume', ticker=args.ticker)
    if args.charts in ('3d', 'all') and 'Volume' in df.columns:
        plotter.plot_3d(df, 'index', 'Close', 'Volume', title='Time vs Price vs Volume', ticker=args.ticker)

    # small sample output + strategy vs buy-and-hold metrics
    print(df[['Close', 'Signal', 'Position', 'Market_Return', 'Strategy_Return']].tail(10))
    print_metrics(df, args.ticker)


if __name__ == "__main__":
    main()
