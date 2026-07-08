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
└── moving-average-crossover/
    ├── strategy.py
    ├── backtest.py
    └── README.md

More strategy folders will be added here as they're built — see "Strategies Coming Soon" below for what's planned.


Each strategy is documented and version-controlled. You can run everything locally (Python + pip) or use [Google Colab](https://colab.research.google.com/) for instant testing.

## 🚀 Getting Started

```bash
git clone https://github.com/VesperaSystems/vespera-strategies.git
cd vespera-strategies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd moving-average-crossover
python strategy.py
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
