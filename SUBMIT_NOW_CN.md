# 现在提交清单

## 1. 项目文件

项目目录：

```text
C:\Users\vieli\Documents\作者监测\bitget-agent-risk-monitor
```

压缩包：

```text
C:\Users\vieli\Documents\作者监测\bitget-agent-risk-monitor.zip
```

## 2. 推荐赛道

Trading Infra

理由：这个项目是给交易 Agent 使用的风控/监控基础设施，不需要真实交易，不需要部署服务器，样例输入输出即可作为 usage record。

## 3. 需要公开的链接

最低提交需要：

- 公开 GitHub 仓库链接
- Demo 视频链接，推荐 1-3 分钟
- X/Twitter 帖子链接，用于参与传播奖和 50 USDT 参与奖

## 4. GitHub 仓库标题

```text
agent-risk-monitor-bitget
```

## 5. GitHub 仓库简介

```text
A lightweight Trading Infra tool that turns crypto trading-agent paper logs into reproducible risk reports.
```

## 6. 表单可填写内容

Project name:

```text
Agent Risk Monitor
```

Track:

```text
Trading Infra
```

Short description:

```text
Agent Risk Monitor is a lightweight Trading Infra tool for AI trading agents. It converts a paper-trading CSV log into a reproducible risk report with PnL, win rate, max drawdown, exposure concentration, loss streaks, anomaly flags, and an agent-readable risk brief. It runs locally with Python standard library only and includes sample input/output files for judge verification.
```

Thesis:

```text
Most autonomous trading agents fail not only because their entry signal is weak, but because they lack a transparent post-trade risk feedback loop. This project provides a small infrastructure layer that helps agents inspect their own trading behavior before live deployment.
```

Usage record:

```text
The repository includes data/sample_trades.csv and generated output files at output/sample_risk_report.json and output/sample_risk_report.html. Judges can reproduce the report by running: python scripts/generate_report.py data/sample_trades.csv --out-dir output
```

Installation / run command:

```bash
python scripts/generate_report.py data/sample_trades.csv --out-dir output
```

## 7. Demo 视频脚本

照着 `docs/demo_script.md` 录即可。最短版本：

1. 打开 GitHub 仓库，说明这是 Trading Infra 项目。
2. 打开 `data/sample_trades.csv`，展示样例交易记录。
3. 运行生成命令。
4. 打开 `output/sample_risk_report.html`，展示风险报告。
5. 打开 `output/sample_risk_report.json`，说明这个结构化输出可以反馈给 Agent。

## 8. X/Twitter 帖子

先引用官方帖：

```text
https://x.com/Bitget_AI/status/2062506424085917944?s=20
```

然后发：

```text
Building Agent Risk Monitor for #BitgetHackathon @Bitget_AI.

It is a lightweight Trading Infra tool that turns a crypto trading agent's paper-trading log into a reproducible risk report: PnL, drawdown, win rate, concentration, loss streaks, anomaly flags, and an agent-readable brief.

No real capital required. The goal is to give trading agents a feedback loop before live deployment.
```

## 9. 提交表单

优先使用官方文档 Submission Requirements 里的链接：

```text
https://forms.gle/CEGB6fRtuobD3bCj8
```

如果社区或邮件给的是另一个最新链接，以社区/邮件为准。

