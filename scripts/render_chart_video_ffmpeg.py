"""Render a non-PowerPoint YouTube draft with animated chart visuals via ffmpeg."""

from __future__ import annotations

import argparse
import math
import random
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(".").resolve()
FFMPEG = ROOT / "node_modules/ffmpeg-static/ffmpeg.exe"
FFPROBE = ROOT / "node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe"


SEGMENT_RE = re.compile(r"^###\s+(?P<start>\d+:\d+)-(?P<end>\d+:\d+)\s+-\s+(?P<title>.+)$")


@dataclass(frozen=True)
class Segment:
    start: str
    end: str
    title: str
    text: str


def timestamp_to_seconds(value: str) -> int:
    minutes, seconds = value.split(":", 1)
    return int(minutes) * 60 + int(seconds)


def extract_script(markdown: str) -> str:
    return markdown.split("## Full Script", 1)[1].split("## Chart And B-Roll Notes", 1)[0].strip()


def parse_segments(script: str) -> list[Segment]:
    segments: list[Segment] = []
    current: dict[str, str] | None = None
    body: list[str] = []
    for line in script.splitlines():
        match = SEGMENT_RE.match(line.strip())
        if match:
            if current:
                segments.append(Segment(current["start"], current["end"], current["title"], "\n".join(body).strip()))
            current = {"start": match.group("start"), "end": match.group("end"), "title": match.group("title")}
            body = []
        elif current:
            body.append(line)
    if current:
        segments.append(Segment(current["start"], current["end"], current["title"], "\n".join(body).strip()))
    return segments


def body_summary(segment: Segment) -> str:
    lines = [line.strip() for line in segment.text.splitlines() if line.strip()]
    if len(lines) <= 7:
        return "\n".join(lines)
    return "\n".join(lines[:7])


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True)


def probe_duration(audio_path: Path) -> float:
    completed = subprocess.run(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    return float(completed.stdout.strip())


def q(path: Path) -> str:
    return path.resolve().as_posix().replace(":", r"\:")


def drawtext_textfile(path: Path, *, x: int, y: int, size: int, color: str, enable: str = "") -> str:
    parts = [
        f"drawtext=font='Arial'",
        f"textfile='{q(path)}'",
        f"x={x}",
        f"y={y}",
        f"fontsize={size}",
        f"fontcolor={color}",
        "line_spacing=10",
        "box=1",
        "boxcolor=0x071014@0.55",
        "boxborderw=18",
    ]
    if enable:
        parts.append(f"enable='{enable}'")
    return ":".join(parts)


def generate_candles(count: int = 64) -> list[tuple[float, float, float, float]]:
    random.seed(77)
    price = 2342.0
    rows: list[tuple[float, float, float, float]] = []
    for index in range(count):
        drift = math.sin(index / 6) * 2.5 + (0.35 if index > 28 else -0.1)
        open_price = price
        close = open_price + drift + random.uniform(-4, 4)
        high = max(open_price, close) + random.uniform(2, 9)
        low = min(open_price, close) - random.uniform(2, 9)
        rows.append((open_price, high, low, close))
        price = close + random.uniform(-2, 2)
    return rows


def candle_filters(duration: float) -> list[str]:
    candles = generate_candles()
    values = [value for row in candles for value in row]
    lo, hi = min(values), max(values)
    chart_x, chart_y, chart_w, chart_h = 80, 150, 1240, 560

    def py(price: float) -> int:
        return int(chart_y + (hi - price) / (hi - lo) * chart_h)

    filters: list[str] = []
    step = chart_w / len(candles)
    appear_span = min(duration - 20, 420)
    for index, (open_price, high, low, close) in enumerate(candles):
        x = int(chart_x + index * step + 5)
        wick_x = x + 7
        high_y, low_y = py(high), py(low)
        open_y, close_y = py(open_price), py(close)
        body_y = min(open_y, close_y)
        body_h = max(4, abs(close_y - open_y))
        color = "0x25D695" if close >= open_price else "0xF05D5E"
        appear = 4 + index / max(1, len(candles) - 1) * appear_span
        enable = f"gte(t,{appear:.2f})"
        filters.append(f"drawbox=x={wick_x}:y={high_y}:w=3:h={max(3, low_y-high_y)}:color={color}@0.95:t=fill:enable='{enable}'")
        filters.append(f"drawbox=x={x}:y={body_y}:w=16:h={body_h}:color={color}@0.95:t=fill:enable='{enable}'")
    return filters


def build_filter_script(segments: list[Segment], duration: float, text_dir: Path, output_path: Path) -> None:
    text_dir.mkdir(parents=True, exist_ok=True)
    filters: list[str] = [
        "drawgrid=width=80:height=80:thickness=1:color=0x21423f@0.45",
        "drawbox=x=50:y=110:w=1310:h=640:color=0x071014@0.35:t=fill",
        "drawbox=x=1380:y=110:w=470:h=640:color=0x0b1d1d@0.75:t=fill",
        "drawbox=x=50:y=790:w=1800:h=210:color=0x071014@0.70:t=fill",
        "drawtext=font='Arial':text='XAUUSD EDUCATIONAL SETUP STUDY':x=70:y=35:fontsize=48:fontcolor=0xF6F1D8",
        "drawtext=font='Arial':text='Bias  |  Liquidity  |  Trigger  |  Invalidation  |  Risk':x=1410:y=155:fontsize=31:fontcolor=0xB6E6D2:line_spacing=18",
        "drawtext=font='Arial':text='CHECKLIST':x=1410:y=610:fontsize=58:fontcolor=0x25D695",
        "drawtext=font='Arial':text='Educational only. No signal. No guaranteed result.':x=1410:y=690:fontsize=26:fontcolor=0xF6F1D8",
        "drawbox=x=80:y=425:w=1240:h=2:color=0xF6F1D8@0.30:t=fill",
        "drawbox=x=250:y=210:w=1:h=470:color=0xF6F1D8@0.18:t=fill",
        "drawbox=x=620:y=210:w=1:h=470:color=0xF6F1D8@0.18:t=fill",
        "drawbox=x=990:y=210:w=1:h=470:color=0xF6F1D8@0.18:t=fill",
    ]
    filters.extend(candle_filters(duration))

    for index, segment in enumerate(segments):
        start = timestamp_to_seconds(segment.start)
        end = timestamp_to_seconds(segment.end)
        title_path = text_dir / f"title_{index:02d}.txt"
        body_path = text_dir / f"body_{index:02d}.txt"
        title_path.write_text(segment.title, encoding="utf-8")
        body_path.write_text(body_summary(segment), encoding="utf-8")
        enable = f"between(t,{start},{end})"
        filters.append(drawtext_textfile(title_path, x=80, y=805, size=40, color="0xF6F1D8", enable=enable))
        filters.append(drawtext_textfile(body_path, x=80, y=870, size=28, color="0xFFFFFF", enable=enable))

    output_path.write_text(",".join(filters), encoding="utf-8")


def render_video(audio_path: Path, filter_script: Path, output_path: Path, duration: float) -> None:
    completed = run(
        [
            str(FFMPEG),
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x071014:s=1920x1080:r=6:d={duration:.2f}",
            "-i",
            str(audio_path),
            "-filter_complex_script",
            str(filter_script),
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "32",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render non-PowerPoint chart video")
    parser.add_argument("--script", type=Path, default=Path("outputs/production/S-RC-API-001/long-video-8min.md"))
    parser.add_argument("--audio", type=Path, default=Path("outputs/production/S-RC-API-001/video/voiceover.wav"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/production/S-RC-API-001/video_ffmpeg_chart"))
    args = parser.parse_args()

    if not FFMPEG.exists() or not FFPROBE.exists():
        raise SystemExit("Missing ffmpeg-static or ffprobe-static")
    markdown = args.script.read_text(encoding="utf-8")
    segments = parse_segments(extract_script(markdown))
    duration = probe_duration(args.audio)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    filter_script = args.output_dir / "chart_video_filters.txt"
    output_mp4 = args.output_dir / "S-RC-API-001-chart-video-8min.mp4"
    build_filter_script(segments, duration, args.output_dir / "text", filter_script)
    render_video(args.audio, filter_script, output_mp4, duration)
    print(f"wrote {output_mp4}")
    print(f"duration_seconds={duration:.2f}")
    print(f"bytes={output_mp4.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
