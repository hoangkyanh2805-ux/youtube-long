"""Render a repo-native long-form YouTube draft video from a Markdown script.

This intentionally uses only local Windows TTS + ffmpeg so it can produce a
real MP4 without adding another external video service.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


SEGMENT_RE = re.compile(r"^###\s+(?P<start>\d+:\d+)-(?P<end>\d+:\d+)\s+-\s+(?P<title>.+)$")


@dataclass(frozen=True)
class Segment:
    start_label: str
    end_label: str
    title: str
    text: str


def timestamp_to_seconds(value: str) -> int:
    minutes, seconds = value.split(":", 1)
    return int(minutes) * 60 + int(seconds)


def extract_full_script(markdown: str) -> str:
    if "## Full Script" not in markdown or "## Chart And B-Roll Notes" not in markdown:
        raise ValueError("Markdown must contain Full Script and Chart And B-Roll Notes sections")
    return markdown.split("## Full Script", 1)[1].split("## Chart And B-Roll Notes", 1)[0].strip()


def parse_segments(script_text: str) -> list[Segment]:
    segments: list[Segment] = []
    current: dict[str, str] | None = None
    body: list[str] = []

    for line in script_text.splitlines():
        match = SEGMENT_RE.match(line.strip())
        if match:
            if current:
                segments.append(
                    Segment(
                        current["start"],
                        current["end"],
                        current["title"],
                        "\n".join(body).strip(),
                    )
                )
            current = {
                "start": match.group("start"),
                "end": match.group("end"),
                "title": match.group("title"),
            }
            body = []
            continue
        if current:
            body.append(line)

    if current:
        segments.append(Segment(current["start"], current["end"], current["title"], "\n".join(body).strip()))
    if not segments:
        raise ValueError("No timed script segments found")
    return segments


def clean_narration_text(segments: list[Segment]) -> str:
    lines: list[str] = []
    for segment in segments:
        for raw_line in segment.text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lines.append(line)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def ass_time(seconds: float) -> str:
    centiseconds = int(round(seconds * 100))
    cs = centiseconds % 100
    total_seconds = centiseconds // 100
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def escape_ass(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")


def compact_overlay_text(text: str, max_words: int = 24) -> str:
    words = re.findall(r"[A-Za-z0-9\"']+|[^\sA-Za-z0-9]", text)
    if len(words) <= max_words:
        return " ".join(words).replace(" ,", ",").replace(" .", ".").replace(" ?", "?")
    trimmed = " ".join(words[:max_words]).replace(" ,", ",").replace(" .", ".").replace(" ?", "?")
    return trimmed + "..."


def build_ass(segments: list[Segment], output_path: Path) -> None:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Arial,72,&H00F6F1D8,&H000000FF,&H00101818,&HCC000000,-1,0,0,0,100,100,0,0,1,3,0,8,120,120,90,1
Style: Body,Arial,54,&H00FFFFFF,&H000000FF,&H00101818,&HCC000000,0,0,0,0,100,100,0,0,1,3,0,2,170,170,100,1
Style: Footer,Arial,38,&H00B6E6D2,&H000000FF,&H00101818,&HCC000000,0,0,0,0,100,100,0,0,1,2,0,2,160,160,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for segment in segments:
        start = timestamp_to_seconds(segment.start_label)
        end = timestamp_to_seconds(segment.end_label)
        segment_lines = [line.strip() for line in segment.text.splitlines() if line.strip()]
        if not segment_lines:
            continue

        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(min(start + 4, end))},Title,,0,0,0,,{escape_ass(segment.title)}\n"
        )
        chunk_duration = max(3.5, (end - start) / max(1, len(segment_lines)))
        cursor = start + 4
        for line in segment_lines:
            if cursor >= end:
                break
            chunk_end = min(end, cursor + chunk_duration)
            overlay = compact_overlay_text(line)
            lines.append(f"Dialogue: 1,{ass_time(cursor)},{ass_time(chunk_end)},Body,,0,0,0,,{escape_ass(overlay)}\n")
            cursor = chunk_end
        lines.append(
            f"Dialogue: 2,{ass_time(start)},{ass_time(end)},Footer,,0,0,0,,{escape_ass('Educational only. No signal. No guaranteed result.')}\n"
        )

    output_path.write_text("".join(lines), encoding="utf-8")


def run_checked(command: list[str], *, cwd: Path) -> None:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(command)
            + "\nSTDOUT:\n"
            + completed.stdout
            + "\nSTDERR:\n"
            + completed.stderr
        )


def local_binary(root: Path, relative_path: str, fallback: str) -> str:
    candidate = root / relative_path
    if candidate.exists():
        return str(candidate)
    return fallback


def synthesize_tts(narration_path: Path, output_wav: Path, voice: str, rate: int, workdir: Path) -> None:
    ps1 = output_wav.with_suffix(".tts.ps1")
    script = f"""
Add-Type -AssemblyName System.Speech
$text = Get-Content -LiteralPath '{narration_path.resolve()}' -Raw
$speaker = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$speaker.Rate = {rate}
$speaker.Volume = 100
$speaker.SetOutputToWaveFile('{output_wav.resolve()}')
$speaker.Speak($text)
$speaker.Dispose()
"""
    ps1.write_text(script, encoding="utf-8")
    run_checked(
        [
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps1),
        ],
        cwd=workdir,
    )


def probe_duration(path: Path, workdir: Path, ffprobe_bin: str) -> float:
    completed = subprocess.run(
        [
            ffprobe_bin,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        cwd=workdir,
        text=True,
        capture_output=True,
        check=True,
    )
    return float(completed.stdout.strip())


def render_video(audio_wav: Path, ass_path: Path, output_mp4: Path, duration: float, workdir: Path, ffmpeg_bin: str) -> None:
    vf = (
        "drawgrid=width=120:height=120:thickness=1:color=0x1f4d45@0.30,"
        "drawbox=x=0:y=0:w=iw:h=110:color=0x071014@0.85:t=fill,"
        "drawbox=x=80:y=160:w=1760:h=760:color=0x0b1d1d@0.55:t=fill,"
        f"subtitles='{ass_path.as_posix()}'"
    )
    run_checked(
        [
            ffmpeg_bin,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x071014:s=1920x1080:r=30:d={duration:.2f}",
            "-i",
            str(audio_wav),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "30",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            "-shortest",
            str(output_mp4),
        ],
        cwd=workdir,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render long-form XAUUSD draft video")
    parser.add_argument("--script", type=Path, default=Path("outputs/production/S-RC-API-001/long-video-8min.md"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/production/S-RC-API-001/video"))
    parser.add_argument("--voice", default="Microsoft David Desktop")
    parser.add_argument("--rate", type=int, default=-1)
    args = parser.parse_args()

    root = Path(".").resolve()
    ffmpeg_bin = local_binary(root, "node_modules/ffmpeg-static/ffmpeg.exe", "ffmpeg")
    ffprobe_bin = local_binary(root, "node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe", "ffprobe")
    markdown = args.script.read_text(encoding="utf-8")
    segments = parse_segments(extract_full_script(markdown))

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    narration_path = output_dir / "narration.txt"
    audio_wav = output_dir / "voiceover.wav"
    ass_path = output_dir / "captions.ass"
    output_mp4 = output_dir / "S-RC-API-001-long-video-draft.mp4"

    narration_path.write_text(clean_narration_text(segments), encoding="utf-8")
    build_ass(segments, ass_path)
    if not audio_wav.exists():
        synthesize_tts(narration_path, audio_wav, args.voice, args.rate, root)
    duration = probe_duration(audio_wav, root, ffprobe_bin)
    render_video(audio_wav, ass_path, output_mp4, duration, root, ffmpeg_bin)

    print(f"wrote {output_mp4}")
    print(f"duration_seconds={duration:.2f}")
    print(f"voice={args.voice}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
