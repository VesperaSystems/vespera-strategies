import pandas as pd

def apply_sma_crossover(df, short_window=50, long_window=200):
    """
    Adds short and long SMA columns, and generates a Signal column:
    1 = Buy (Golden Cross), -1 = Sell (Death Cross), 0 = Hold
    """
    df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
    df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()

    df['Signal'] = 0
    df.loc[df['SMA_Short'] > df['SMA_Long'], 'Signal'] = 1
    df.loc[df['SMA_Short'] < df['SMA_Long'], 'Signal'] = -1

    return df