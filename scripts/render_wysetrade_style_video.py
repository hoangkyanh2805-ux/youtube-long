from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "production" / "S-RC-API-002-wysetrade-style"
FRAMES = OUT / "frames"
VIDEO_ONLY = OUT / "S-RC-API-002-visual.mp4"
VOICEOVER = OUT / "voiceover.wav"
FINAL = OUT / "S-RC-API-002-wysetrade-style-candles.mp4"
SCRIPT_JSON = OUT / "script_segments.json"
WIDTH, HEIGHT = 1920, 1080
FPS = 24


SEGMENTS = [
    {
        "duration": 18,
        "title": "READ CANDLES FAST",
        "body": "A candle is not a signal. It is a story of buyers and sellers.",
        "vo": "In this video, I am going to show you how to read candlestick charts fast, using XAUUSD examples for education only. A candle is not a signal. It is a story of buyers and sellers.",
        "kind": "intro",
    },
    {
        "duration": 34,
        "title": "BULLISH VS BEARISH",
        "body": "Green closes above open. Red closes below open.",
        "vo": "Start with the basics. A bullish candle closes above where it opened. A bearish candle closes below where it opened. Do not overcomplicate it. The body tells you who controlled that period.",
        "kind": "bull_bear",
    },
    {
        "duration": 42,
        "title": "BODY = CONTROL",
        "body": "Large body: strong control. Small body: hesitation.",
        "vo": "The body is the first clue. A large body means one side controlled most of the time period. A small body means price moved, but neither side finished with strong control.",
        "kind": "body",
    },
    {
        "duration": 44,
        "title": "WICKS = REJECTION",
        "body": "Wicks show where price tried to go and failed.",
        "vo": "The wick is the second clue. A wick shows where price travelled, but could not hold. A long upper wick tells you buyers pushed higher, then sellers rejected that area. A long lower wick tells you sellers pushed lower, then buyers rejected that area.",
        "kind": "wicks",
    },
    {
        "duration": 36,
        "title": "DOJI = INDECISION",
        "body": "Open and close near the same price.",
        "vo": "When the open and close are almost the same, you are looking at indecision. Buyers and sellers fought, but neither side finished clearly in control. That does not mean enter. It means pay attention to context.",
        "kind": "doji",
    },
    {
        "duration": 42,
        "title": "CONTEXT MATTERS",
        "body": "Same candle, different meaning at different locations.",
        "vo": "The same candle can mean different things depending on location. A rejection candle in the middle of a range is weaker. A rejection candle after a sweep of a high or low is more meaningful. Candlesticks matter most when you read them at important levels.",
        "kind": "context",
    },
    {
        "duration": 38,
        "title": "TIMEFRAME CHANGES THE STORY",
        "body": "One daily candle can contain many one-hour candles.",
        "vo": "Every candle represents a time period. On a daily chart, one candle is one day. On a one hour chart, one candle is one hour. Before you judge a candle, know what time period it represents.",
        "kind": "timeframe",
    },
    {
        "duration": 46,
        "title": "PRICE ACTION = STORY",
        "body": "Body + wick + location + trend.",
        "vo": "Price action is the story created by candles together. Do not read one candle alone. Read the body, the wick, the location, and the trend. That is how you stop reacting to every candle and start reading the market.",
        "kind": "story",
    },
    {
        "duration": 40,
        "title": "XAUUSD CHECKLIST",
        "body": "Bias. Liquidity. Trigger. Invalidation. Risk.",
        "vo": "For XAUUSD, use this checklist before studying any setup. Bias. Liquidity. Trigger. Invalidation. Risk. If you cannot explain those five points, you are not reading price action yet. You are guessing.",
        "kind": "checklist",
    },
    {
        "duration": 18,
        "title": "COMMENT CHECKLIST",
        "body": "Educational only. No signal. No guaranteed result.",
        "vo": "Comment CHECKLIST if you want the educational prep list. This is not a signal and it does not guarantee any result. It is a framework for studying candles with a written plan.",
        "kind": "outro",
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill: str, bold: bool = False) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill)


def centered(draw: ImageDraw.ImageDraw, y: int, value: str, size: int, fill: str, bold: bool = False) -> None:
    f = font(size, bold)
    box = draw.textbbox((0, 0), value, font=f)
    draw.text(((WIDTH - (box[2] - box[0])) // 2, y), value, font=f, fill=fill)


def candle(draw: ImageDraw.ImageDraw, x: int, y_mid: int, body_h: int, wick_h: int, color: str, w: int = 70) -> None:
    top = y_mid - body_h // 2
    bottom = y_mid + body_h // 2
    draw.line((x, y_mid - wick_h // 2, x, y_mid + wick_h // 2), fill=color, width=10)
    draw.rounded_rectangle((x - w // 2, top, x + w // 2, bottom), radius=8, fill=color)


def grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(110, WIDTH - 80, 140):
        draw.line((x, 170, x, 880), fill="#18212b", width=2)
    for y in range(190, 880, 95):
        draw.line((90, y, WIDTH - 80, y), fill="#18212b", width=2)


def draw_scene(segment: dict, progress: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0b1118")
    draw = ImageDraw.Draw(img)
    grid(draw)
    draw.rectangle((0, 0, WIDTH, 120), fill="#070b10")
    text(draw, (88, 36), segment["title"], 44, "#f8fafc", True)
    text(draw, (88, 92), segment["body"], 24, "#93a4b8")
    draw.rounded_rectangle((1560, 34, 1828, 78), radius=8, fill="#13202c", outline="#26394b", width=2)
    centered(draw, 40, "XAUUSD EDUCATION", 22, "#ffd166", True)

    kind = segment["kind"]
    if kind in {"intro", "story"}:
        for i in range(16):
            x = 220 + i * 90
            phase = math.sin(i * 0.8 + progress * 4)
            color = "#22c55e" if phase > -0.1 else "#ef4444"
            candle(draw, x, int(550 - phase * 80), 70 + int(abs(phase) * 80), 210, color, 52)
        draw.line((220, 640, 1580, 370), fill="#ffd166", width=5)
    elif kind == "bull_bear":
        candle(draw, 610, 535, 300, 560, "#22c55e", 130)
        candle(draw, 1260, 535, 300, 560, "#ef4444", 130)
        centered(draw, 845, "BULLISH: CLOSE ABOVE OPEN", 36, "#22c55e", True)
        text(draw, (1120, 845), "BEARISH: CLOSE BELOW OPEN", 36, "#ef4444", True)
    elif kind == "body":
        candle(draw, 500, 550, 420, 500, "#22c55e", 140)
        candle(draw, 930, 550, 120, 500, "#ffd166", 140)
        candle(draw, 1360, 550, 420, 500, "#ef4444", 140)
        centered(draw, 860, "BODY SIZE SHOWS CONTROL", 42, "#f8fafc", True)
    elif kind == "wicks":
        candle(draw, 650, 560, 110, 600, "#22c55e", 130)
        candle(draw, 1230, 560, 110, 600, "#ef4444", 130)
        draw.line((650, 245, 840, 245), fill="#ffd166", width=5)
        draw.line((1230, 875, 1040, 875), fill="#ffd166", width=5)
        text(draw, (850, 222), "UPPER REJECTION", 34, "#ffd166", True)
        text(draw, (720, 846), "LOWER REJECTION", 34, "#ffd166", True)
    elif kind == "doji":
        candle(draw, 960, 560, 28, 600, "#e5e7eb", 150)
        centered(draw, 850, "OPEN ≈ CLOSE", 52, "#ffd166", True)
    elif kind == "context":
        for i, x in enumerate(range(280, 1540, 120)):
            color = "#22c55e" if i % 3 != 0 else "#ef4444"
            candle(draw, x, 670 - i * 22, 110 + (i % 4) * 40, 260, color, 60)
        draw.rounded_rectangle((1220, 210, 1610, 300), radius=10, outline="#ffd166", width=5)
        text(draw, (1245, 232), "IMPORTANT LEVEL", 34, "#ffd166", True)
    elif kind == "timeframe":
        candle(draw, 570, 540, 480, 680, "#22c55e", 170)
        for i in range(9):
            x = 990 + i * 65
            color = "#22c55e" if i in {0, 1, 4, 6, 7, 8} else "#ef4444"
            candle(draw, x, 650 - i * 35, 70, 170, color, 36)
        text(draw, (420, 850), "1D CANDLE", 40, "#f8fafc", True)
        text(draw, (980, 850), "MANY 1H CANDLES", 40, "#f8fafc", True)
    elif kind == "checklist":
        items = ["BIAS", "LIQUIDITY", "TRIGGER", "INVALIDATION", "RISK"]
        for i, item in enumerate(items):
            y = 275 + i * 105
            draw.rounded_rectangle((520, y, 1400, y + 70), radius=10, fill="#101c28", outline="#26394b", width=2)
            draw.rounded_rectangle((545, y + 18, 580, y + 53), radius=4, fill="#ffd166")
            text(draw, (620, y + 14), item, 34, "#f8fafc", True)
    elif kind == "outro":
        centered(draw, 360, "COMMENT CHECKLIST", 86, "#ffd166", True)
        centered(draw, 475, "Educational only. No signal.", 42, "#f8fafc")
        centered(draw, 540, "No guaranteed result.", 42, "#f8fafc")

    draw.rectangle((86, 920, 1834, 968), fill="#070b10")
    draw.rectangle((86, 920, 86 + int(1748 * progress), 968), fill="#ffd166")
    return img


def write_voiceover() -> None:
    text_path = OUT / "voiceover.txt"
    text_path.write_text(" ".join(segment["vo"] for segment in SEGMENTS), encoding="utf-8")
    ps1 = OUT / "render_voiceover.ps1"
    ps1.write_text(
        "\n".join(
            [
                "Add-Type -AssemblyName System.Speech",
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
                "$s.Rate = -1",
                "$s.Volume = 100",
                f"$s.SetOutputToWaveFile('{str(VOICEOVER)}')",
                f"$text = Get-Content -LiteralPath '{str(text_path)}' -Raw",
                "$s.Speak($text)",
                "$s.Dispose()",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.check_call(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps1)])


def render_frames() -> float:
    FRAMES.mkdir(parents=True, exist_ok=True)
    current = 0
    timeline = []
    for segment in SEGMENTS:
        frames = int(segment["duration"] * FPS)
        start_frame = current
        for i in range(frames):
            progress = i / max(frames - 1, 1)
            img = draw_scene(segment, progress)
            img.save(FRAMES / f"frame_{current:06d}.jpg", quality=92)
            current += 1
        timeline.append({**segment, "start": start_frame / FPS, "end": current / FPS})
    SCRIPT_JSON.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return current / FPS


def render_video(duration: float) -> None:
    ffmpeg = ROOT / "node_modules" / "ffmpeg-static" / "ffmpeg.exe"
    subprocess.check_call(
        [
            str(ffmpeg),
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(FRAMES / "frame_%06d.jpg"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            str(VIDEO_ONLY),
        ]
    )
    write_voiceover()
    subprocess.check_call(
        [
            str(ffmpeg),
            "-y",
            "-i",
            str(VIDEO_ONLY),
            "-i",
            str(VOICEOVER),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(FINAL),
        ]
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    duration = render_frames()
    render_video(duration)
    print(json.dumps({"video": str(FINAL), "duration": duration, "segments": len(SEGMENTS)}, indent=2))


if __name__ == "__main__":
    main()
