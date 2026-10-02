from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VECTCUT = ROOT / "tools" / "VectCutAPI"
CAPCUT_ROOT = Path(
    os.environ.get("CAPCUT_MCP_DRAFT_ROOT")
    or Path(os.environ["LOCALAPPDATA"]) / "CapCut" / "User Data" / "Projects" / "com.lveditor.draft"
)
SOURCE_VIDEO = ROOT / "outputs" / "production" / "S-RC-API-001" / "video_ffmpeg_chart" / "S-RC-API-001-chart-video-8min.mp4"
DEFAULT_OUTPUT_BASE = ROOT / "outputs" / "capcut_drafts"
PROJECT_PREFIX = "S-RC-API-001-CapCut"


def _bootstrap_paths() -> None:
    ffmpeg_dir = ROOT / "node_modules" / "ffmpeg-static"
    ffprobe_dir = ROOT / "node_modules" / "ffprobe-static" / "bin" / "win32" / "x64"
    os.environ["PATH"] = f"{ffmpeg_dir};{ffprobe_dir};{os.environ.get('PATH', '')}"
    sys.path.insert(0, str(VECTCUT))


def _duration_seconds(path: Path) -> float:
    ffprobe = ROOT / "node_modules" / "ffprobe-static" / "bin" / "win32" / "x64" / "ffprobe.exe"
    cmd = [
        str(ffprobe),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


def _project_name() -> str:
    return f"{PROJECT_PREFIX}-{time.strftime('%Y%m%d-%H%M%S')}"


def _update_capcut_manifest(project_name: str, project_dir: Path, duration: float) -> str:
    meta_path = CAPCUT_ROOT / "root_meta_info.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    now_us = int(time.time() * 1_000_000)
    draft_id = str(uuid.uuid4()).upper()
    forward_project_dir = project_dir.as_posix()
    forward_root = CAPCUT_ROOT.as_posix()

    entries = [
        entry
        for entry in meta.get("all_draft_store", [])
        if entry.get("draft_name") != project_name and Path(entry.get("draft_fold_path", "")) != project_dir
    ]

    entry = {
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": str(project_dir / "draft_cover.jpg").replace("\\", "/"),
        "draft_fold_path": forward_project_dir,
        "draft_id": draft_id,
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_infinite_canvas_draft": False,
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_json_file": str(project_dir / "draft_content.json").replace("\\", "/"),
        "draft_name": project_name,
        "draft_new_version": "",
        "draft_root_path": forward_root,
        "draft_timeline_materials_size": SOURCE_VIDEO.stat().st_size,
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "pippit_avatar_url": "",
        "pippit_extra_info": "",
        "pippit_id": "",
        "pippit_user_name": "",
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "tm_draft_removed": 0,
        "tm_duration": int(duration * 1_000_000),
    }
    meta["all_draft_store"] = [entry] + entries
    meta["draft_ids"] = max(int(meta.get("draft_ids") or 0), len(meta["all_draft_store"]))
    meta["root_path"] = forward_root

    backup = meta_path.with_name(f"root_meta_info.{time.strftime('%Y%m%d-%H%M%S')}.bak.json")
    shutil.copy2(meta_path, backup)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return draft_id


def build(project_name: str | None = None, output_base: Path = DEFAULT_OUTPUT_BASE) -> dict:
    _bootstrap_paths()
    from add_text_impl import add_text_impl
    from add_video_track import add_video_track
    from save_draft_impl import save_draft_impl

    if not SOURCE_VIDEO.is_file():
        raise FileNotFoundError(f"Missing source video: {SOURCE_VIDEO}")

    project_name = project_name or _project_name()
    output_base.mkdir(parents=True, exist_ok=True)
    duration = _duration_seconds(SOURCE_VIDEO)

    video = add_video_track(
        video_url=str(SOURCE_VIDEO),
        draft_folder=str(output_base),
        width=1920,
        height=1080,
        start=0,
        end=duration,
        target_start=0,
        duration=duration,
        track_name="main",
        volume=1.0,
    )
    draft_id = video["draft_id"]

    overlays = [
        (0, 7, "XAUUSD CHECKLIST - NO SIGNAL, EDUCATIONAL ONLY", -0.82),
        (42, 52, "FRAMEWORK: TREND -> ZONE -> TRIGGER -> RISK", 0.80),
        (118, 128, "WAIT FOR CONFIRMATION. NO CHASE.", 0.80),
        (205, 215, "INVALIDATION FIRST, TARGET SECOND.", 0.80),
        (320, 330, "SCREENSHOT BEFORE ENTRY.", 0.80),
        (455, min(duration, 486), "COMMENT CHECKLIST FOR THE TEMPLATE", -0.82),
    ]
    for start, end, text, y in overlays:
        if start >= duration:
            continue
        add_text_impl(
            text=text,
            start=start,
            end=min(end, duration),
            draft_id=draft_id,
            transform_y=y,
            transform_x=0,
            font_color="#FFD166",
            font_size=7.5,
            border_width=0.08,
            background_alpha=0.28,
            background_color="#000000",
            fixed_width=0.90,
            line_spacing=0.2,
            bold=True,
        )

    saved = save_draft_impl(
        draft_id=draft_id,
        draft_folder=str(output_base),
        project_name=project_name,
        auto_deploy=True,
    )
    project_dir = CAPCUT_ROOT / project_name
    manifest_id = _update_capcut_manifest(project_name, project_dir, duration)
    return {
        "project_name": project_name,
        "vectcut_draft_id": draft_id,
        "manifest_draft_id": manifest_id,
        "project_dir": str(project_dir),
        "source_video": str(SOURCE_VIDEO),
        "duration_seconds": duration,
        "save_result": saved,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name", default=None)
    parser.add_argument("--output-base", default=str(DEFAULT_OUTPUT_BASE))
    args = parser.parse_args()
    result = build(args.project_name, Path(args.output_base))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
