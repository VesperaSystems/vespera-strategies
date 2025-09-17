import argparse
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from mpl_toolkits.mplot3d import Axes3D  # for static 3D
import plotly.graph_objs as go
import plotly.io as pio

from strategy import apply_sma_crossover  # 👈 this is your strategy logic

TRADING_DAYS = 252  # typical business days in a year

def sharpe_ratio(returns, rf=0.0, periods=TRADING_DAYS):
    """
    Calculate the annualized Sharpe Ratio of a returns series.
    :param returns: Series of returns (periodic, e.g. daily)
    :param rf: Annual risk-free rate (decimal)
    :param periods: Number of periods per year (default 252)
    :return: Annualized Sharpe Ratio
    """
    # convert annual rf to per-period
    excess = returns - rf / periods
    mu = excess.mean()
    sigma = excess.std(ddof=0)
    return 0.0 if sigma == 0 else (mu / sigma) * np.sqrt(periods)


def max_drawdown(equity_curve):
    """
    Calculate the maximum drawdown of an equity curve.
    :param equity_curve: Series of equity values
    :return: Maximum drawdown (as a percentage)
    """
    roll_max = equity_curve.cummax()
    dd = equity_curve / roll_max - 1.0
    return dd.min()


def fetch_stock_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    return df


def compute_backtest(df):
    # Signal must already exist from strategy
    df = df.copy()
    if 'Signal' not in df.columns:
        raise KeyError("DataFrame must contain 'Signal' column from strategy.apply_sma_crossover")
    df['Position'] = df['Signal'].shift(1).fillna(0)  # act *after* the signal
    df['Market_Return'] = df['Close'].pct_change().fillna(0)
    df['Strategy_Return'] = df['Position'] * df['Market_Return']
    df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
    df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()
    return df


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


def plot_performance(df, ticker, plotter):
    # 1D: cumulative returns
    plotter.plot_time_series(df, ['Cumulative_Market', 'Cumulative_Strategy'], title='Backtest vs Market', ticker=ticker)

    # 2D: price vs volume colored by daily returns
    if 'Volume' in df.columns:
        df2 = df.copy()
        if 'Market_Return' not in df2.columns:
            df2['Market_Return'] = df2['Close'].pct_change().fillna(0)
        plotter.plot_2d_scatter(df2, 'Close', 'Volume', color_col='Market_Return', title='Price vs Volume (colored by daily return)', ticker=ticker)

    # 3D: time, price, volume
    if 'Volume' in df.columns:
        plotter.plot_3d(df, 'index', 'Close', 'Volume', title='Time vs Price vs Volume', ticker=ticker)


def main():
    parser = argparse.ArgumentParser(description="Backtest and plot (static/interactive).")
    parser.add_argument("--ticker", default="PLTR")
    parser.add_argument("--start", default="2015-01-01")
    parser.add_argument("--end", default="2024-01-01")
    parser.add_argument("--interactive", action="store_true", help="Use Plotly interactive plotting")
    parser.add_argument("--charts", choices=['1d', '2d', '3d', 'all'], default='all')
    args = parser.parse_args()

    df = fetch_stock_data(args.ticker, args.start, args.end)
    df = apply_sma_crossover(df)
    df = compute_backtest(df)

    mode = 'interactive' if args.interactive else 'static'
    plotter = Plotter(mode=mode)

    if args.charts in ('1d', 'all'):
        plotter.plot_time_series(df, ['Cumulative_Market', 'Cumulative_Strategy'], title='Backtest vs Market', ticker=args.ticker)
    if args.charts in ('2d', 'all') and 'Volume' in df.columns:
        plotter.plot_2d_scatter(df, 'Close', 'Volume', color_col='Market_Return' if 'Market_Return' in df.columns else None, title='Price vs Volume', ticker=args.ticker)
    if args.charts in ('3d', 'all') and 'Volume' in df.columns:
        plotter.plot_3d(df, 'index', 'Close', 'Volume', title='Time vs Price vs Volume', ticker=args.ticker)

    # small sample output
    print(df[['Close', 'Signal', 'Position', 'Market_Return', 'Strategy_Return']].tail(10))


if __name__ == "__main__":
    main()