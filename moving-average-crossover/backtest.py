import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from strategy import apply_sma_crossover  # 👈 this is your strategy logic


def fetch_stock_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    return df


def compute_backtest(df):
    # Signal must already exist from strategy
    df['Position'] = df['Signal'].shift(1)  # act *after* the signal

    df['Market_Return'] = df['Close'].pct_change() #what the market actually did
    df['Strategy_Return'] = df['Position'] * df['Market_Return'] #had we acted on the strategy

    df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
    df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()

    return df


def plot_performance(df, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Cumulative_Market'], label='Market Return', linestyle='--')
    plt.plot(df['Cumulative_Strategy'], label='Strategy Return')
    plt.title(f'Backtest vs Market – {ticker}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    ticker = "PLTR"
    start_date = "2015-01-01"
    end_date = "2024-01-01"

    df = fetch_stock_data(ticker, start_date, end_date)
    df = apply_sma_crossover(df) 
    df = compute_backtest(df)
    plot_performance(df, ticker)

    print(df[['Close', 'Signal', 'Position', 'Market_Return', 'Strategy_Return']].tail(10))


if __name__ == "__main__":
    main()