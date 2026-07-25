# 🧠 Vespera Strategies

Welcome to the **open lab** of [Vespera Systems](https://vesperasystems.com) — a DIY, punk-inspired quant trading project reclaiming finance through code, curiosity, and courage.

This repository contains algorithmic trading strategies built from first principles. Every strategy folder includes:
- 📜 Python source code (`.py`) and/or Jupyter notebooks (`.ipynb`)
- 📊 Backtests and visualizations
- ✅ Clear, testable logic
- 📓 Mathematical or financial theory (where applicable)

## 📂 Structure

/vespera-strategies
│
├── vespera_strategies/          ← shared library (data, metrics, strategies)
│   ├── data.py                  ← market data fetching (yfinance)
│   ├── metrics.py               ← Sharpe, CAGR, max drawdown, summaries
│   ├── ma_crossover.py          ← MA crossover signals + backtest
│   └── reporting.py             ← push results to Vespera Mission Control
│
├── moving-average-crossover/
│   ├── strategy.ipynb           ← 📓 learning notebook (open in Colab!)
│   ├── strategy.py
│   ├── backtest.py              ← CLI: plots + metrics
│   └── README.md
│
├── runner.py                    ← scheduled signal runner (see docs/deployment.md)
├── Dockerfile                   ← containerized runner for any cloud
└── pyproject.toml               ← pip-installable, incl. from Colab

More strategy folders will be added here as they're built — see "Strategies Coming Soon" below for what's planned.

Each strategy is documented and version-controlled. The core logic lives in the `vespera_strategies` package so the **same code** powers the notebooks, the CLI scripts, and the scheduled signal runner.

## 🚀 Getting Started

**Instant (no setup):** open a strategy notebook in Colab, e.g.
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/VesperaSystems/vespera-strategies/blob/main/moving-average-crossover/strategy.ipynb)

**Locally:**

```bash
git clone https://github.com/VesperaSystems/vespera-strategies.git
cd vespera-strategies
python3 -m venv .venv
source .venv/bin/activate
pip install -e . plotly
python moving-average-crossover/backtest.py --ticker SPY --start 2015-01-01 --charts 1d
```

## 🧠 Philosophy

“Mental models and reflexes.”
We build muscle memory and math intuition from scratch.
You don’t need a PhD — just VS Code, a terminal, and the will to learn.

📚 Strategies Coming Soon
	•	✅ Moving Average Crossover (Golden Cross / Death Cross)
	•	🔜 RSI + Bollinger Band Divergence
	•	🔜 Volatility Breakout (ATR-based)
	•	🔜 Mean Reversion using Z-score
	•	🔜 Statistical Arbitrage (Pairs Trading)

🛠 Tools
	•	Python 3
	•	pandas, numpy, matplotlib
	•	Google Colab + Jupyter
	•	GitHub for versioned backtesting

🕶 About Vespera

Vespera is an independent, open quant lab — no suits, no secrets.
Follow our build-in-public journey:
🧠 vesperasystems.com

📜 License

MIT — fork freely, trade responsibly.
