# Submission Description

## 1. Project Name

Agent Risk Monitor

## 2. Track

Trading Infra

## 3. Core Thesis

Autonomous trading agents need a feedback loop before they are allowed to trade with real capital. A strategy can generate entries and exits, but without post-trade diagnostics it cannot reliably understand whether losses came from signal quality, excessive concentration, bad stop placement, or repeated re-entry after failed trades.

Agent Risk Monitor is lightweight infrastructure for that feedback loop. It turns a trading agent's paper-trading log into structured risk metrics, anomaly flags, and an agent-readable brief. The tool is designed to help builders inspect and improve agent behavior before live deployment.

## 4. What It Does

The tool accepts a CSV trading log with timestamp, pair, direction, price, quantity, balance change, balance after, and trade reason. It then calculates:

- Net PnL
- Win rate
- Gross profit and loss
- Average trade PnL
- Max drawdown
- Total notional exposure
- Symbol concentration
- Direction mix
- Longest loss streak
- A 0-100 risk score
- Practical anomaly flags

It outputs both JSON and HTML reports. The JSON can be passed to another agent, and the HTML report can be reviewed by humans.

## 5. Verifiable Usage Record

The repository includes a sample input and generated output:

- `data/sample_trades.csv`
- `output/sample_risk_report.json`
- `output/sample_risk_report.html`

Judges can reproduce the output with:

```bash
python scripts/generate_report.py data/sample_trades.csv --out-dir output
```

## 6. Current Result

On the included paper-trading sample, the monitor analyzes 18 trades across BTCUSDT, ETHUSDT, SOLUSDT, and DOGEUSDT. It reports positive net PnL, a moderate risk score, and flags the loss streak as the main issue for the next strategy iteration.

## 7. Why It Matters

This project does not try to replace a trading strategy. Instead, it provides the infrastructure that makes strategy agents safer and easier to iterate. A trading agent can run a paper-trading session, export its trades, and use this tool to understand what needs to change before real capital is involved.

## 8. Limitations

The current version uses sample paper-trading data and transparent rule-based diagnostics. Future versions could connect directly to Bitget Agent Hub, ingest live paper-trading records, and feed the report back into a strategy agent automatically.

