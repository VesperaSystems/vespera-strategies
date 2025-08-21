# Moving Average Crossover Strategy

## 📈 Summary

A trend-following strategy based on the crossover of two Simple Moving Averages (SMA).

- **Short SMA (50-day)**
- **Long SMA (200-day)**

A **Golden Cross** occurs when the short SMA crosses above the long SMA → **Buy signal**  
A **Death Cross** occurs when the short SMA crosses below the long SMA → **Sell signal**

---

## 🧮 Formula

$$
\text{SMA}_n(t) = \frac{1}{n} \sum_{i=0}^{n-1} P(t - i)
$$

Where:
- \( P(t) \) is the closing price at time \( t \)
- \( n \) is the window size (e.g., 50, 200)

---

## 📊 Backtest Assumptions

| Assumption                  | Description |
|----------------------------|-------------|
| ✅ One position at a time  | Long only (shorting coming later) |
| ✅ All-in/All-out trades   | No position sizing or scaling |
| ✅ Close price used        | Trades executed on next day close |
| ❌ No slippage or delays   | Unrealistic, will add later |
| ❌ No trading fees         | Ignored for now |
| ❌ No taxes considered     | To be included in a future pass |
| ❌ No volume confirmation  | Currently price-only signal |

---

## 🧠 Status

| Component           | Status      |
|---------------------|-------------|
| Strategy logic      | ✅ Implemented |
| Signal generation   | ✅ Implemented |
| Backtesting engine  | ✅ Basic cumulative returns via `.cumprod()` |
| Visualisation       | ✅ Signals + price chart |
| Performance metrics | ❌ Coming next (sharpe, drawdown, etc) |

---

## 📎 Limitations

- Crossover strategies often break in sideways markets.
- This model does **not** yet confirm signals using volume or volatility.
- Trade timing assumes **perfect next-day execution**.
- Backtest assumes you **see and act on every signal** — not always realistic.
- No capital efficiency, portfolio-level logic, or universe ranking is in play.

---

## 🧪 How to Run

```bash
pip install pandas matplotlib yfinance
python3 strategy.py
```
---

## 📘 Next Steps
- Add proper backtest.py for trade simulation and PnL
- Compare with a buy-and-hold benchmark
- Introduce short-side logic (Death Cross → short)
- Apply to other tickers
- Wrap into a reusable function/class

---

## 🤘 Ethos

This repo is part of the Vespera Systems quant lab.
We’re DIY. We’re math-forward. We trade ideas, not buzzwords.