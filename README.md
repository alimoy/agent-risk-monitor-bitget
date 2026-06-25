# Agent Risk Monitor

Agent Risk Monitor is a lightweight Trading Infra project for the Bitget AI Base Camp Hackathon. It turns a crypto trading agent's paper-trading log into a reproducible risk report with drawdown, win rate, exposure concentration, loss streaks, anomaly flags, and an agent-readable risk brief.

The project is intentionally zero-cost and zero-dependency: it runs locally with Python 3 and uses a sample paper-trading log. No real capital, exchange account, paid server, or API key is required.

## Track

Trading Infra

## Core Thesis

Most autonomous trading agents fail in production not only because their entry signal is weak, but because they lack a transparent risk feedback loop. A trading agent needs infrastructure that can inspect its own trading record, summarize risk, and produce structured feedback before real deployment.

Agent Risk Monitor provides that missing layer. It accepts a trade log, computes risk metrics, flags suspicious behavior, and creates a report that a human judge or another agent can read and reproduce.

## Features

- Reads paper-trading records from CSV
- Computes PnL, win rate, gross profit/loss, max drawdown, notional exposure, direction mix, and symbol concentration
- Detects practical risk issues such as loss streaks, over-concentration, and high drawdown
- Generates both JSON and HTML reports
- Includes sample input and output files for verifiable usage
- Runs offline with Python standard library only

## Repository Structure

```text
.
├── data/
│   └── sample_trades.csv
├── docs/
│   ├── demo_script.md
│   ├── submission_description.md
│   └── tweet_draft.md
├── index.html
├── output/
│   ├── sample_risk_report.html
│   └── sample_risk_report.json
├── scripts/
│   └── generate_report.py
└── README.md
```

## Quick Start

```bash
python scripts/generate_report.py data/sample_trades.csv --out-dir output
```

Then open:

```text
output/sample_risk_report.html
```

## Sample Input

The sample paper-trading log is available at:

```text
data/sample_trades.csv
```

Required columns:

```text
timestamp,pair,direction,price,quantity,balance_change,balance_after,reason
```

## Sample Output

The reproducible usage record is available at:

```text
output/sample_risk_report.json
output/sample_risk_report.html
```

These files were generated from the sample input with the command in Quick Start.

## Demo Video

Chinese demo video:

```text
output/agent_risk_monitor_demo_cn.mp4
```

## Example Result

For the included sample trading record, the monitor reports:

- 18 paper trades
- Net PnL: 436.90 USDT
- Win rate: 61.11%
- Max drawdown: 1.65%
- Risk score: 33 / 100
- Risk level: Moderate

## Why It Helps Trading Agents

This project is not a trading strategy. It is infrastructure for trading agents. A strategy agent can run, export its trade log, and use this monitor as a feedback step before live deployment. The output can also be used as context for a coding agent or strategy agent when improving the next strategy version.

## Reproducibility

The project has no external dependencies and no hidden data source. Judges can reproduce the report by running the command above.

## Limitations

- The sample data is paper-trading data, not live exchange execution data.
- The report is risk-focused and does not place orders.
- The anomaly checks are intentionally simple and transparent for hackathon review.
