#!/usr/bin/env python3
"""Create the Chinese demo MP4 for the hackathon submission."""

from __future__ import annotations

import json
import math
import subprocess
import textwrap
import wave
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output"
ASSET_DIR = OUT_DIR / "demo_assets"
VIDEO_NO_AUDIO = OUT_DIR / "agent_risk_monitor_demo_cn_no_audio.mp4"
VIDEO_FINAL = OUT_DIR / "agent_risk_monitor_demo_cn.mp4"
AUDIO_WAV = OUT_DIR / "agent_risk_monitor_demo_cn.wav"

WIDTH = 1280
HEIGHT = 720
FPS = 24


NARRATION = [
    (
        "项目介绍",
        "大家好，这是 Agent Risk Monitor，一个为 Bitget AI Hackathon Trading Infra 赛道准备的轻量级风控监控工具。",
        "它的目标不是直接下单，而是给交易 Agent 提供一个上线前的风险反馈环。",
    ),
    (
        "为什么需要它",
        "很多自动交易 Agent 的问题，不只是入场信号不够好，而是缺少对交易结果的复盘能力。",
        "这个项目不需要真实资金，不需要交易所 API，也不需要服务器。",
    ),
    (
        "样例输入",
        "这里是样例输入文件 data/sample_trades.csv。",
        "每一行包含时间、交易对、方向、价格、数量、账户余额变化、交易后余额，以及 Agent 当时的交易理由。",
    ),
    (
        "一条命令生成报告",
        "运行方式很简单：执行 python scripts/generate_report.py data/sample_trades.csv --out-dir output。",
        "脚本会生成两个文件：一个 JSON 报告和一个 HTML 报告。",
    ),
    (
        "HTML 风险报告",
        "现在看 HTML 报告。这个样例一共有 18 笔纸面交易，覆盖 BTC、ETH、SOL 和 DOGE。",
        "报告会展示净收益、胜率、最大回撤、风险分数、最长连续亏损，以及交易对集中度。",
    ),
    (
        "关键结果",
        "在这个样例里，净收益是 436.90 USDT，胜率是 61.11%，最大回撤是 1.65%。",
        "风险分数是 33 分，风险等级是中等。",
    ),
    (
        "异常提示",
        "系统识别出的主要问题是连续亏损达到 3 笔。",
        "所以建议加入冷却规则，避免 Agent 在连续失败后反复重新入场。",
    ),
    (
        "JSON 可给 Agent 读取",
        "再看 JSON 报告。它保存了同样的指标和异常提示。",
        "这个结构化输出可以直接作为上下文传给另一个 Agent，用来改进下一版策略。",
    ),
    (
        "总结",
        "Agent Risk Monitor 是一个很小但可运行的交易基础设施模块。",
        "它让交易 Agent 在真实资金上线前，先拥有一个可复现、可检查、可反馈的风险评估流程。",
    ),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "msyhbd.ttc" if bold else "msyh.ttc"
    path = Path("C:/Windows/Fonts") / name
    if not path.exists():
        path = Path("C:/Windows/Fonts/simhei.ttf")
    if not path.exists():
        path = Path("C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size)


FONT_TITLE = font(40, True)
FONT_H2 = font(26, True)
FONT_BODY = font(23)
FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 20)
FONT_SMALL = font(18)


def read_lines(path: Path, limit: int) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()[:limit]


def load_report() -> dict:
    return json.loads((OUT_DIR / "sample_risk_report.json").read_text(encoding="utf-8"))


def wrap_cn(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for char in paragraph:
            if len(current) >= width:
                lines.append(current)
                current = char
            else:
                current += char
        if current:
            lines.append(current)
    return lines


def draw_rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str, outline: str | None = None) -> None:
    draw.rounded_rectangle(xy, radius=8, fill=fill, outline=outline, width=1)


def draw_text_block(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int, fill: str, font_obj: ImageFont.FreeTypeFont, line_gap: int = 8) -> int:
    x, y = xy
    max_chars = max(12, width // 24)
    for line in wrap_cn(text, max_chars):
        draw.text((x, y), line, fill=fill, font=font_obj)
        y += font_obj.size + line_gap
    return y


def base_slide(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#f5f7f8")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 74), fill="#0c838d")
    draw.text((44, 20), "Agent Risk Monitor", fill="white", font=FONT_H2)
    draw.text((44, 104), title, fill="#172024", font=FONT_TITLE)
    draw.text((44, 154), subtitle, fill="#5f6f76", font=FONT_BODY)
    return img, draw


def draw_repo_slide(title: str, a: str, b: str) -> Image.Image:
    img, draw = base_slide(title, "Trading Infra | Bitget AI Hackathon")
    left = (44, 210, 492, 626)
    right = (520, 210, 1236, 626)
    draw_rounded(draw, left, "#ffffff", "#dce4e7")
    draw_rounded(draw, right, "#ffffff", "#dce4e7")
    draw.text((68, 236), "公开仓库内容", fill="#172024", font=FONT_H2)
    files = [
        "README.md",
        "data/sample_trades.csv",
        "scripts/generate_report.py",
        "output/sample_risk_report.html",
        "output/sample_risk_report.json",
        "docs/demo_script_cn.md",
    ]
    y = 286
    for item in files:
        draw.text((82, y), item, fill="#233035", font=FONT_BODY)
        y += 42
    draw.text((548, 236), "核心说明", fill="#172024", font=FONT_H2)
    draw_text_block(draw, (548, 286), a + "\n" + b, 640, "#233035", FONT_BODY)
    return img


def draw_csv_slide(title: str, a: str, b: str) -> Image.Image:
    img, draw = base_slide(title, "样例输入：纸面交易日志")
    draw_rounded(draw, (44, 202, 1236, 618), "#ffffff", "#dce4e7")
    lines = read_lines(ROOT / "data" / "sample_trades.csv", 10)
    y = 226
    for i, line in enumerate(lines):
        fill = "#0c838d" if i == 0 else "#172024"
        draw.text((66, y), line[:124], fill=fill, font=FONT_MONO)
        y += 34
    draw.rectangle((44, 628, 1236, 692), fill="#e8f5f7")
    draw_text_block(draw, (68, 640), a + " " + b, 1120, "#172024", FONT_SMALL, 4)
    return img


def draw_command_slide(title: str, a: str, b: str) -> Image.Image:
    img, draw = base_slide(title, "本地可复现，无需 API Key")
    draw_rounded(draw, (90, 245, 1190, 360), "#172024", "#172024")
    draw.text((124, 288), "python scripts/generate_report.py data/sample_trades.csv --out-dir output", fill="#ffffff", font=FONT_MONO)
    draw_rounded(draw, (90, 404, 1190, 560), "#ffffff", "#dce4e7")
    draw.text((124, 434), "输出文件", fill="#172024", font=FONT_H2)
    draw.text((150, 482), "output/sample_risk_report.json", fill="#0c838d", font=FONT_BODY)
    draw.text((150, 522), "output/sample_risk_report.html", fill="#0c838d", font=FONT_BODY)
    draw_text_block(draw, (90, 600), a + " " + b, 1040, "#5f6f76", FONT_SMALL, 4)
    return img


def draw_report_slide(title: str, a: str, b: str, detail: str = "") -> Image.Image:
    report = load_report()
    metrics = report["metrics"]
    img, draw = base_slide(title, "HTML 风险报告摘要")
    cards = [
        ("交易数", str(metrics["trade_count"])),
        ("净收益", f"{metrics['net_pnl_usdt']:.2f} USDT"),
        ("胜率", f"{metrics['win_rate']:.2%}"),
        ("最大回撤", f"{metrics['max_drawdown']:.2%}"),
        ("风险分数", f"{metrics['risk_score']}/100"),
        ("风险等级", "中等"),
    ]
    x0, y0 = 44, 220
    for idx, (label, value) in enumerate(cards):
        x = x0 + (idx % 3) * 398
        y = y0 + (idx // 3) * 138
        draw_rounded(draw, (x, y, x + 360, y + 104), "#ffffff", "#dce4e7")
        draw.text((x + 24, y + 18), label, fill="#5f6f76", font=FONT_SMALL)
        draw.text((x + 24, y + 48), value, fill="#172024", font=FONT_H2)
    draw_rounded(draw, (44, 514, 1236, 632), "#ffffff", "#dce4e7")
    draw.text((70, 540), "异常提示", fill="#172024", font=FONT_H2)
    flag = report["anomaly_flags"][0]
    draw_text_block(draw, (70, 580), flag if not detail else detail, 1080, "#233035", FONT_SMALL, 4)
    draw_text_block(draw, (44, 652), a + " " + b, 1140, "#5f6f76", FONT_SMALL, 4)
    return img


def draw_json_slide(title: str, a: str, b: str) -> Image.Image:
    img, draw = base_slide(title, "结构化输出可以继续喂给策略 Agent")
    draw_rounded(draw, (44, 190, 1236, 640), "#172024", "#172024")
    data = load_report()
    snippet = {
        "risk_score": data["metrics"]["risk_score"],
        "risk_level": data["metrics"]["risk_level"],
        "win_rate": data["metrics"]["win_rate"],
        "max_drawdown": data["metrics"]["max_drawdown"],
        "anomaly_flags": data["anomaly_flags"],
    }
    lines = json.dumps(snippet, ensure_ascii=False, indent=2).splitlines()
    y = 220
    for line in lines:
        draw.text((72, y), line, fill="#ffffff", font=FONT_MONO)
        y += 32
    draw_text_block(draw, (44, 660), a + " " + b, 1140, "#5f6f76", FONT_SMALL, 4)
    return img


def draw_closing_slide(title: str, a: str, b: str) -> Image.Image:
    img, draw = base_slide(title, "可复现、可检查、可反馈")
    draw_rounded(draw, (150, 230, 1130, 560), "#ffffff", "#dce4e7")
    draw.text((200, 280), "给交易 Agent 的上线前风险反馈环", fill="#172024", font=FONT_TITLE)
    points = ["不需要真实资金", "不需要交易所 API", "样例输入输出可复现", "JSON 可继续传给另一个 Agent"]
    y = 360
    for point in points:
        draw.text((230, y), point, fill="#233035", font=FONT_BODY)
        y += 46
    draw_text_block(draw, (150, 604), a + " " + b, 900, "#5f6f76", FONT_SMALL, 4)
    return img


def create_audio() -> float | None:
    text = " ".join(part for _, *parts in NARRATION for part in parts)
    ps = f"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SelectVoice('Microsoft Huihui Desktop')
$s.Rate = 0
$s.Volume = 100
$s.SetOutputToWaveFile('{str(AUDIO_WAV).replace("'", "''")}')
$s.Speak('{text.replace("'", "''")}')
$s.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    with wave.open(str(AUDIO_WAV), "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def make_slides() -> list[Image.Image]:
    slide_builders = [
        draw_repo_slide,
        draw_repo_slide,
        draw_csv_slide,
        draw_command_slide,
        draw_report_slide,
        draw_report_slide,
        lambda title, a, b: draw_report_slide(title, a, b, "连续亏损达到 3 笔；建议加入冷却规则，避免失败后反复重新入场。"),
        draw_json_slide,
        draw_closing_slide,
    ]
    return [builder(title, a, b) for builder, (title, a, b) in zip(slide_builders, NARRATION)]


def create_video(slides: list[Image.Image], audio_duration: float | None) -> None:
    if audio_duration is None:
        durations = [12.0] * len(slides)
    else:
        durations = [audio_duration / len(slides)] * len(slides)

    writer = imageio.get_writer(
        VIDEO_NO_AUDIO,
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=1,
    )
    for slide, duration in zip(slides, durations):
        frames = max(1, int(math.ceil(duration * FPS)))
        frame = np.asarray(slide)
        for _ in range(frames):
            writer.append_data(frame)
    writer.close()


def mux_audio() -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(VIDEO_NO_AUDIO),
        "-i",
        str(AUDIO_WAV),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(VIDEO_FINAL),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    ASSET_DIR.mkdir(exist_ok=True)
    audio_duration = create_audio()
    slides = make_slides()
    for idx, slide in enumerate(slides, start=1):
        slide.save(ASSET_DIR / f"slide_{idx:02d}.png")
    create_video(slides, audio_duration)
    mux_audio()
    print(f"Created {VIDEO_FINAL}")
    print(f"Duration target: {audio_duration:.1f} seconds")


if __name__ == "__main__":
    main()
