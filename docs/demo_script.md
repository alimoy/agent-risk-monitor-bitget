# 3-Minute Demo Script

## 0:00 - 0:20

Show the repository. Mention that this is a Trading Infra project for AI trading agents and that it runs locally without real capital or API keys.

## 0:20 - 0:45

Open `data/sample_trades.csv`. Explain that it is a paper-trading log with timestamp, pair, direction, price, quantity, balance change, balance after, and reason.

## 0:45 - 1:15

Run:

```bash
python scripts/generate_report.py data/sample_trades.csv --out-dir output
```

Show that the JSON and HTML reports are generated.

## 1:15 - 2:15

Open `output/sample_risk_report.html`. Walk through:

- trade count
- net PnL
- win rate
- max drawdown
- risk score
- anomaly flags
- pair concentration

## 2:15 - 2:45

Open `output/sample_risk_report.json`. Explain that another agent can consume this structured output as feedback for strategy improvement.

## 2:45 - 3:00

Close with the thesis: trading agents need a reproducible risk feedback loop before live deployment. This project is a small, runnable infrastructure layer for that loop.

