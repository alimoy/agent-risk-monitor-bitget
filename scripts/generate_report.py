#!/usr/bin/env python3
"""Generate a reproducible risk report from a trading-agent CSV log."""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


REQUIRED_COLUMNS = {
    "timestamp",
    "pair",
    "direction",
    "price",
    "quantity",
    "balance_change",
    "balance_after",
    "reason",
}


@dataclass
class Trade:
    timestamp: str
    pair: str
    direction: str
    price: float
    quantity: float
    balance_change: float
    balance_after: float
    reason: str

    @property
    def notional(self) -> float:
        return abs(self.price * self.quantity)


def parse_trade(row: dict[str, str]) -> Trade:
    return Trade(
        timestamp=row["timestamp"].strip(),
        pair=row["pair"].strip().upper(),
        direction=row["direction"].strip().lower(),
        price=float(row["price"]),
        quantity=float(row["quantity"]),
        balance_change=float(row["balance_change"]),
        balance_after=float(row["balance_after"]),
        reason=row["reason"].strip(),
    )


def load_trades(path: Path) -> list[Trade]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"Missing required columns: {missing_text}")
        trades = [parse_trade(row) for row in reader]
    if not trades:
        raise ValueError("The trade log is empty.")
    return trades


def max_drawdown(balance_curve: list[float]) -> float:
    peak = balance_curve[0]
    worst = 0.0
    for balance in balance_curve:
        peak = max(peak, balance)
        if peak > 0:
            worst = max(worst, (peak - balance) / peak)
    return worst


def longest_loss_streak(trades: list[Trade]) -> int:
    current = 0
    longest = 0
    for trade in trades:
        if trade.balance_change < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def concentration_by_pair(trades: list[Trade]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for trade in trades:
        totals[trade.pair] += trade.notional
    grand_total = sum(totals.values()) or 1.0
    return {
        pair: round(notional / grand_total, 4)
        for pair, notional in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    }


def build_report(trades: list[Trade], source_file: str) -> dict:
    pnl_values = [trade.balance_change for trade in trades]
    wins = [value for value in pnl_values if value > 0]
    losses = [value for value in pnl_values if value < 0]
    balance_curve = [trade.balance_after for trade in trades]
    pair_concentration = concentration_by_pair(trades)
    top_pair = next(iter(pair_concentration))
    top_pair_share = pair_concentration[top_pair]
    loss_streak = longest_loss_streak(trades)
    drawdown = max_drawdown(balance_curve)
    net_pnl = sum(pnl_values)
    total_notional = sum(trade.notional for trade in trades)
    win_rate = len(wins) / len(trades)

    flags: list[str] = []
    if drawdown >= 0.05:
        flags.append("Max drawdown is above 5%; reduce position size or add a hard daily stop.")
    if loss_streak >= 3:
        flags.append("Loss streak reached 3 or more trades; add a cool-down rule after repeated losses.")
    if top_pair_share >= 0.60:
        flags.append(f"Exposure is concentrated in {top_pair}; diversify or cap symbol-level allocation.")
    if len(losses) and abs(mean(losses)) > max(mean(wins) if wins else 0.0, 1.0):
        flags.append("Average loss is larger than average win; review stop placement and take-profit logic.")
    if not flags:
        flags.append("No critical anomaly detected in the sample period.")

    risk_score = 0
    risk_score += min(35, int(drawdown * 500))
    risk_score += min(20, max(0, loss_streak - 1) * 8)
    risk_score += min(20, int(max(0.0, top_pair_share - 0.35) * 80))
    risk_score += min(15, int((1 - win_rate) * 20))
    risk_score += 10 if net_pnl < 0 else 0
    risk_score = min(100, risk_score)

    if risk_score < 30:
        risk_level = "Low"
    elif risk_score < 60:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    summary = (
        f"The agent completed {len(trades)} paper trades across {len(pair_concentration)} symbols. "
        f"Net PnL was {net_pnl:.2f} USDT with a {win_rate:.2%} win rate and "
        f"{drawdown:.2%} max drawdown. The current risk level is {risk_level.lower()} "
        f"with a score of {risk_score}/100. The next iteration should focus on "
        f"loss-streak controls, symbol concentration limits, and better confirmation "
        f"before re-entering after a stopped trade."
    )

    return {
        "project": "Agent Risk Monitor",
        "track": "Trading Infra",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": source_file,
        "metrics": {
            "trade_count": len(trades),
            "symbols": sorted(pair_concentration),
            "net_pnl_usdt": round(net_pnl, 2),
            "gross_profit_usdt": round(sum(wins), 2),
            "gross_loss_usdt": round(sum(losses), 2),
            "win_rate": round(win_rate, 4),
            "average_trade_pnl_usdt": round(mean(pnl_values), 2),
            "max_drawdown": round(drawdown, 4),
            "total_notional_usdt": round(total_notional, 2),
            "longest_loss_streak": loss_streak,
            "direction_mix": dict(Counter(trade.direction for trade in trades)),
            "pair_concentration": pair_concentration,
            "risk_score": risk_score,
            "risk_level": risk_level,
        },
        "anomaly_flags": flags,
        "agent_brief": summary,
        "trades": [trade.__dict__ | {"notional": round(trade.notional, 2)} for trade in trades],
    }


def render_html(report: dict) -> str:
    metrics = report["metrics"]
    flag_items = "\n".join(f"<li>{html.escape(flag)}</li>" for flag in report["anomaly_flags"])
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(trade['timestamp'])}</td>"
        f"<td>{html.escape(trade['pair'])}</td>"
        f"<td>{html.escape(trade['direction'])}</td>"
        f"<td>{trade['price']:.4f}</td>"
        f"<td>{trade['quantity']:.6f}</td>"
        f"<td>{trade['balance_change']:.2f}</td>"
        f"<td>{trade['balance_after']:.2f}</td>"
        f"<td>{html.escape(trade['reason'])}</td>"
        "</tr>"
        for trade in report["trades"]
    )
    concentration = "\n".join(
        f"<li>{html.escape(pair)}: {share:.2%}</li>"
        for pair, share in metrics["pair_concentration"].items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Risk Monitor Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7f8;
      --panel: #ffffff;
      --ink: #172024;
      --muted: #5f6f76;
      --accent: #0c838d;
      --line: #dce4e7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.1;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); margin: 0; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 22px 0;
    }}
    .metric, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(23, 32, 36, 0.04);
    }}
    .metric {{
      padding: 16px;
      min-height: 94px;
    }}
    .label {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .value {{
      display: block;
      font-weight: 750;
      font-size: 24px;
    }}
    section {{
      padding: 18px;
      margin-top: 14px;
    }}
    ul {{ margin: 8px 0 0; padding-left: 20px; }}
    li {{ margin: 6px 0; }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 900px;
      font-size: 13px;
      background: #fff;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 650;
      background: #f9fbfb;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 3px 10px;
      border-radius: 999px;
      color: #fff;
      background: var(--accent);
      font-size: 13px;
      font-weight: 700;
    }}
    @media (max-width: 820px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      main {{ padding: 24px 14px 36px; }}
      .grid {{ grid-template-columns: 1fr; }}
      .value {{ font-size: 22px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <span class="badge">{html.escape(metrics["risk_level"])} Risk</span>
      <h1>Agent Risk Monitor Report</h1>
      <p>Generated from {html.escape(report["source_file"])} for the Bitget AI Base Camp Hackathon Trading Infra track.</p>
    </header>

    <div class="grid">
      <div class="metric"><span class="label">Trades</span><span class="value">{metrics["trade_count"]}</span></div>
      <div class="metric"><span class="label">Net PnL</span><span class="value">{metrics["net_pnl_usdt"]:.2f} USDT</span></div>
      <div class="metric"><span class="label">Win Rate</span><span class="value">{metrics["win_rate"]:.2%}</span></div>
      <div class="metric"><span class="label">Max Drawdown</span><span class="value">{metrics["max_drawdown"]:.2%}</span></div>
      <div class="metric"><span class="label">Risk Score</span><span class="value">{metrics["risk_score"]}/100</span></div>
      <div class="metric"><span class="label">Total Notional</span><span class="value">{metrics["total_notional_usdt"]:.2f}</span></div>
      <div class="metric"><span class="label">Loss Streak</span><span class="value">{metrics["longest_loss_streak"]}</span></div>
      <div class="metric"><span class="label">Symbols</span><span class="value">{len(metrics["symbols"])}</span></div>
    </div>

    <section>
      <h2>Agent Brief</h2>
      <p>{html.escape(report["agent_brief"])}</p>
    </section>

    <section>
      <h2>Anomaly Flags</h2>
      <ul>{flag_items}</ul>
    </section>

    <section>
      <h2>Pair Concentration</h2>
      <ul>{concentration}</ul>
    </section>

    <section>
      <h2>Trade Log</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Pair</th>
              <th>Direction</th>
              <th>Price</th>
              <th>Quantity</th>
              <th>Balance Change</th>
              <th>Balance After</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def write_report(report: dict, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "sample_risk_report.json"
    html_path = out_dir / "sample_risk_report.html"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    return json_path, html_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an agent risk report from a CSV trade log.")
    parser.add_argument("csv_path", type=Path, help="Path to the trade CSV file.")
    parser.add_argument("--out-dir", type=Path, default=Path("output"), help="Directory for generated reports.")
    args = parser.parse_args()

    trades = load_trades(args.csv_path)
    report = build_report(trades, str(args.csv_path))
    json_path, html_path = write_report(report, args.out_dir)
    print(f"Wrote {json_path}")
    print(f"Wrote {html_path}")
    print(f"Risk level: {report['metrics']['risk_level']} ({report['metrics']['risk_score']}/100)")


if __name__ == "__main__":
    main()

