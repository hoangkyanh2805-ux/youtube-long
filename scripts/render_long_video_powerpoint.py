"""Render the 8-minute long video as a PowerPoint-exported MP4.

This is a local fallback for Windows machines without a working ffmpeg binary.
It creates a real MP4 draft with timed slides and a separate voiceover WAV.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


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


def extract_full_script(markdown: str) -> str:
    return markdown.split("## Full Script", 1)[1].split("## Chart And B-Roll Notes", 1)[0].strip()


def parse_segments(script_text: str) -> list[Segment]:
    segments: list[Segment] = []
    current: dict[str, str] | None = None
    body: list[str] = []
    for line in script_text.splitlines():
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
    if not segments:
        raise ValueError("No timed segments found")
    return segments


def segment_duration(segment: Segment) -> int:
    return timestamp_to_seconds(segment.end) - timestamp_to_seconds(segment.start)


def segment_body(segment: Segment) -> str:
    lines = [line.strip() for line in segment.text.splitlines() if line.strip()]
    return "\n".join(lines[:9])


def build_slides(segments: list[Segment]) -> list[dict[str, object]]:
    slides: list[dict[str, object]] = [
        {
            "title": "Do This Before Following Any Live XAUUSD Setup",
            "body": "5 boxes before any live setup:\nBias\nLiquidity\nTrigger\nInvalidation\nRisk",
            "footer": "Educational only. No signal. No guaranteed result.",
            "duration": 8,
        }
    ]
    for segment in segments:
        slides.append(
            {
                "title": f"{segment.start}-{segment.end}  {segment.title}",
                "body": segment_body(segment),
                "footer": "Educational only. No signal. No guaranteed result.",
                "duration": segment_duration(segment),
            }
        )
    slides.append(
        {
            "title": "Comment CHECKLIST",
            "body": "Get the educational XAUUSD prep list.\nUse it before studying a setup.\nNo signal. No guaranteed result.",
            "footer": "S-RC-API-001 draft video",
            "duration": 10,
        }
    )
    return slides


def clean_narration_text(segments: list[Segment]) -> str:
    parts: list[str] = []
    for segment in segments:
        for line in segment.text.splitlines():
            clean = line.strip()
            if clean:
                parts.append(clean)
        parts.append("")
    return "\n".join(parts).strip() + "\n"


def write_powershell_renderer(slides_json: Path, pptx_path: Path, mp4_path: Path, ps1_path: Path) -> None:
    script = f"""
$ErrorActionPreference = 'Stop'
$slides = Get-Content -LiteralPath '{slides_json.resolve()}' -Raw | ConvertFrom-Json
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = -1
$presentation = $ppt.Presentations.Add()
$presentation.PageSetup.SlideSize = 13
$presentation.PageSetup.SlideWidth = 1920
$presentation.PageSetup.SlideHeight = 1080

foreach ($item in $slides) {{
    $slide = $presentation.Slides.Add($presentation.Slides.Count + 1, 12)
    $bg = $slide.Shapes.AddShape(1, 0, 0, 1920, 1080)
    $bg.Fill.ForeColor.RGB = 1316359
    $bg.Line.Visible = 0

    $panel = $slide.Shapes.AddShape(1, 90, 150, 1740, 760)
    $panel.Fill.ForeColor.RGB = 1973790
    $panel.Fill.Transparency = 0.08
    $panel.Line.ForeColor.RGB = 7459444
    $panel.Line.Weight = 2

    for ($x = 120; $x -lt 1820; $x += 160) {{
        $line = $slide.Shapes.AddLine($x, 150, $x, 910)
        $line.Line.ForeColor.RGB = 3108910
        $line.Line.Transparency = 0.55
    }}
    for ($y = 190; $y -lt 900; $y += 120) {{
        $line = $slide.Shapes.AddLine(90, $y, 1830, $y)
        $line.Line.ForeColor.RGB = 3108910
        $line.Line.Transparency = 0.55
    }}

    $title = $slide.Shapes.AddTextbox(1, 110, 62, 1700, 90)
    $title.TextFrame.TextRange.Text = [string]$item.title
    $title.TextFrame.TextRange.Font.Name = 'Arial'
    $title.TextFrame.TextRange.Font.Size = 46
    $title.TextFrame.TextRange.Font.Bold = -1
    $title.TextFrame.TextRange.Font.Color.RGB = 14217710
    $title.TextFrame.WordWrap = -1

    $body = $slide.Shapes.AddTextbox(1, 150, 210, 1620, 610)
    $body.TextFrame.TextRange.Text = [string]$item.body
    $body.TextFrame.TextRange.Font.Name = 'Arial'
    $body.TextFrame.TextRange.Font.Size = 38
    $body.TextFrame.TextRange.Font.Color.RGB = 16777215
    $body.TextFrame.WordWrap = -1
    $body.TextFrame.AutoSize = 0

    $footer = $slide.Shapes.AddTextbox(1, 150, 940, 1620, 60)
    $footer.TextFrame.TextRange.Text = [string]$item.footer
    $footer.TextFrame.TextRange.Font.Name = 'Arial'
    $footer.TextFrame.TextRange.Font.Size = 28
    $footer.TextFrame.TextRange.Font.Color.RGB = 13821650

    $slide.SlideShowTransition.AdvanceOnTime = -1
    $slide.SlideShowTransition.AdvanceTime = [double]$item.duration
}}

$presentation.SaveAs('{pptx_path.resolve()}')
$presentation.CreateVideo('{mp4_path.resolve()}', $true, 5, 1080, 30, 85)
$tries = 0
while ($tries -lt 240) {{
    $status = $presentation.CreateVideoStatus
    Write-Output ("CreateVideoStatus=" + $status)
    if ((Test-Path -LiteralPath '{mp4_path.resolve()}') -and ((Get-Item -LiteralPath '{mp4_path.resolve()}').Length -gt 0) -and ($status -ne 1) -and ($status -ne 2)) {{
        break
    }}
    if ($status -eq 4) {{
        throw 'PowerPoint video export failed'
    }}
    Start-Sleep -Seconds 3
    $tries += 1
}}
if (-not (Test-Path -LiteralPath '{mp4_path.resolve()}')) {{
    throw 'PowerPoint video export did not create an MP4 file'
}}
try {{ $presentation.Close() }} catch {{ Write-Output ("cleanup_warning=" + $_.Exception.Message) }}
try {{ $ppt.Quit() }} catch {{ Write-Output ("quit_warning=" + $_.Exception.Message) }}
"""
    ps1_path.write_text(script, encoding="utf-8")


def write_powershell_tts(narration_path: Path, wav_path: Path, ps1_path: Path, rate: int) -> None:
    script = f"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$text = Get-Content -LiteralPath '{narration_path.resolve()}' -Raw
$speaker = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$speaker.Rate = {rate}
$speaker.Volume = 100
$speaker.SetOutputToWaveFile('{wav_path.resolve()}')
$speaker.Speak($text)
$speaker.Dispose()
"""
    ps1_path.write_text(script, encoding="utf-8")


def run_ps1(ps1_path: Path) -> None:
    completed = subprocess.run(
        [
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps1_path),
        ],
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render long video using PowerPoint")
    parser.add_argument("--script", type=Path, default=Path("outputs/production/S-RC-API-001/long-video-8min.md"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/production/S-RC-API-001/video"))
    parser.add_argument("--rate", type=int, default=-1)
    args = parser.parse_args()

    markdown = args.script.read_text(encoding="utf-8")
    segments = parse_segments(extract_full_script(markdown))
    slides = build_slides(segments)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    slides_json = output_dir / "slides.json"
    narration_path = output_dir / "narration.txt"
    pptx_path = output_dir / "S-RC-API-001-long-video-draft.pptx"
    mp4_path = output_dir / "S-RC-API-001-long-video-draft.mp4"
    voiceover_path = output_dir / "voiceover.wav"
    render_ps1 = output_dir / "render_powerpoint_video.ps1"
    tts_ps1 = output_dir / "render_voiceover.ps1"

    slides_json.write_text(json.dumps(slides, indent=2, ensure_ascii=False), encoding="utf-8")
    narration_path.write_text(clean_narration_text(segments), encoding="utf-8")

    write_powershell_tts(narration_path, voiceover_path, tts_ps1, args.rate)
    try:
        run_ps1(tts_ps1)
    except RuntimeError as exc:
        print(f"voiceover_warning={exc}")

    write_powershell_renderer(slides_json, pptx_path, mp4_path, render_ps1)
    run_ps1(render_ps1)

    print(f"wrote {mp4_path}")
    print(f"wrote {pptx_path}")
    if voiceover_path.exists():
        print(f"wrote {voiceover_path}")
    print(f"slides={len(slides)}")
    print(f"timed_duration_seconds={sum(int(slide['duration']) for slide in slides)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
