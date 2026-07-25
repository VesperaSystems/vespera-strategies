# Moving Average Crossover Strategy

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/VesperaSystems/vespera-strategies/blob/main/moving-average-crossover/strategy.ipynb)

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
| Strategy logic      | ✅ Shared module: `vespera_strategies/ma_crossover.py` |
| Signal generation   | ✅ Implemented, incl. crossover event detection |
| Backtesting engine  | ✅ Basic cumulative returns via `.cumprod()` |
| Visualisation       | ✅ Signals + price chart |
| Performance metrics | ✅ Sharpe, CAGR, max drawdown, buy-and-hold benchmark |
| Learning notebook   | ✅ `strategy.ipynb` (Colab badge above) |

---

## 📎 Limitations

- Crossover strategies often break in sideways markets.
- This model does **not** yet confirm signals using volume or volatility.
- Trade timing assumes **perfect next-day execution**.
- Backtest assumes you **see and act on every signal** — not always realistic.
- No capital efficiency, portfolio-level logic, or universe ranking is in play.

---

## 🧪 How to Run

**Zero setup:** click the Colab badge at the top of this README.

**Locally:**

```bash
# from the repo root
python3 -m venv .venv && source .venv/bin/activate
pip install -e . plotly
python moving-average-crossover/backtest.py --ticker AAPL --start 2018-01-01 --charts 1d
```

Or use the library directly:

```python
from vespera_strategies import run_ma_crossover
df, summary = run_ma_crossover("SPY", start="2015-01-01")
print(summary["metrics"], summary["latest_signal"])
```

---

## 📘 Next Steps
- Introduce short-side logic (Death Cross → short)
- Add slippage and trading fees to the backtest
- Volume confirmation for signals
- Parameter sweep: which SMA windows hold up across tickers?

---

## 🤘 Ethos

This repo is part of the Vespera Systems quant lab.
We’re DIY. We’re math-forward. We trade ideas, not buzzwords.