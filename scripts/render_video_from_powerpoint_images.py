"""Export PowerPoint slides to PNGs, then assemble MP4 with ffmpeg-static."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(".").resolve()
VIDEO_DIR = Path("outputs/production/S-RC-API-001/video")
PPTX = VIDEO_DIR / "S-RC-API-001-long-video-draft.pptx"
SLIDES_JSON = VIDEO_DIR / "slides.json"
VOICEOVER = VIDEO_DIR / "voiceover.wav"
IMAGE_DIR = VIDEO_DIR / "slides_png"
CONCAT_FILE = VIDEO_DIR / "slides_concat.txt"
OUTPUT_MP4 = VIDEO_DIR / "S-RC-API-001-long-video-draft.mp4"
FFMPEG = ROOT / "node_modules/ffmpeg-static/ffmpeg.exe"


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)


def export_slides_ps1(ps1_path: Path) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    script = f"""
$ErrorActionPreference = 'Stop'
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = -1
$presentation = $ppt.Presentations.Open('{PPTX.resolve()}', $false, $false, $false)
$out = '{IMAGE_DIR.resolve()}'
New-Item -ItemType Directory -Force -Path $out | Out-Null
for ($i = 1; $i -le $presentation.Slides.Count; $i++) {{
    $path = Join-Path $out ('slide_' + $i.ToString('000') + '.png')
    $presentation.Slides.Item($i).Export($path, 'PNG', 1920, 1080)
}}
try {{ $presentation.Close() }} catch {{ Write-Output ('cleanup_warning=' + $_.Exception.Message) }}
try {{ $ppt.Quit() }} catch {{ Write-Output ('quit_warning=' + $_.Exception.Message) }}
"""
    ps1_path.write_text(script, encoding="utf-8")
    run(
        [
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps1_path),
        ]
    )


def write_concat_file() -> None:
    slides = json.loads(SLIDES_JSON.read_text(encoding="utf-8"))
    image_paths = sorted(IMAGE_DIR.glob("slide_*.png"))
    if len(image_paths) != len(slides):
        raise RuntimeError(f"Expected {len(slides)} slide images, found {len(image_paths)}")

    lines: list[str] = []
    for image_path, slide in zip(image_paths, slides):
        safe_path = image_path.resolve().as_posix()
        lines.append(f"file '{safe_path}'")
        lines.append(f"duration {int(slide['duration'])}")
    lines.append(f"file '{image_paths[-1].resolve().as_posix()}'")
    CONCAT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_mp4() -> None:
    if not FFMPEG.exists():
        raise RuntimeError(f"Missing ffmpeg-static binary: {FFMPEG}")
    run(
        [
            str(FFMPEG),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(CONCAT_FILE),
            "-i",
            str(VOICEOVER),
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
            "-shortest",
            "-movflags",
            "+faststart",
            str(OUTPUT_MP4),
        ]
    )


def main() -> int:
    if not PPTX.exists():
        raise SystemExit(f"Missing PPTX: {PPTX}")
    if not SLIDES_JSON.exists():
        raise SystemExit(f"Missing slides JSON: {SLIDES_JSON}")
    if not VOICEOVER.exists():
        raise SystemExit(f"Missing voiceover WAV: {VOICEOVER}")

    export_slides_ps1(VIDEO_DIR / "export_slide_images.ps1")
    write_concat_file()
    render_mp4()
    print(f"wrote {OUTPUT_MP4}")
    print(f"slides={len(json.loads(SLIDES_JSON.read_text(encoding='utf-8')))}")
    print(f"bytes={OUTPUT_MP4.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
