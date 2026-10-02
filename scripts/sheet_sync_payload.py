"""Build auditable Google Sheets batchUpdate payloads from local CSV outputs."""

from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SheetSyncTarget:
    name: str
    csv_path: Path
    sheet_id: int
    max_data_rows: int
    start_row_index: int = 0
    start_column_index: int = 0


DEFAULT_TARGETS = [
    SheetSyncTarget("Video Inventory", Path("data/processed/video_inventory.csv"), 1006, 100),
    SheetSyncTarget("Remake Candidates", Path("data/processed/remake_candidates.csv"), 1005, 100),
    SheetSyncTarget("Shorts Pipeline", Path("outputs/content/content_calendar.csv"), 1003, 20),
]


def prefer_existing(root: Path, preferred: Path, fallback: Path) -> Path:
    preferred_path = root / preferred
    if preferred_path.exists():
        return preferred_path
    return root / fallback


def resolve_default_targets(root: Path) -> list[SheetSyncTarget]:
    return [
        SheetSyncTarget(
            "Video Inventory",
            prefer_existing(root, Path("data/processed/video_inventory_api.csv"), Path("data/processed/video_inventory.csv")),
            1006,
            100,
        ),
        SheetSyncTarget(
            "Remake Candidates",
            prefer_existing(root, Path("data/processed/remake_candidates_api.csv"), Path("data/processed/remake_candidates.csv")),
            1005,
            100,
        ),
        SheetSyncTarget("Shorts Pipeline", root / "outputs/content/content_calendar.csv", 1003, 20),
    ]


def read_limited_csv_text(path: Path, max_data_rows: int) -> tuple[str, int, int]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if not rows:
        raise ValueError(f"{path} is empty")

    header = rows[:1]
    data_rows = rows[1 : max_data_rows + 1]
    selected_rows = header + data_rows

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(selected_rows)
    return output.getvalue().rstrip("\n"), len(data_rows), len(header[0])


def build_paste_data_request(target: SheetSyncTarget) -> tuple[dict, dict]:
    csv_text, written_rows, column_count = read_limited_csv_text(target.csv_path, target.max_data_rows)
    request = {
        "pasteData": {
            "coordinate": {
                "sheetId": target.sheet_id,
                "rowIndex": target.start_row_index,
                "columnIndex": target.start_column_index,
            },
            "type": "PASTE_NORMAL",
            "delimiter": ",",
            "data": csv_text,
        }
    }
    summary = {
        "target": target.name,
        "csv_path": str(target.csv_path),
        "sheet_id": target.sheet_id,
        "written_rows": written_rows,
        "column_count": column_count,
        "max_data_rows": target.max_data_rows,
    }
    return request, summary


def build_sync_payload(targets: Iterable[SheetSyncTarget]) -> dict:
    requests: list[dict] = []
    summary: list[dict] = []
    for target in targets:
        request, item = build_paste_data_request(target)
        requests.append(request)
        summary.append(item)
    return {"requests": requests, "summary": summary}


def write_payload_files(payload: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_path = output_dir / "sheet_sync_payload.json"
    summary_path = output_dir / "sheet_sync_summary.md"
    payload_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(render_summary(payload["summary"]), encoding="utf-8")
    return payload_path, summary_path


def render_summary(summary: list[dict]) -> str:
    lines = [
        "# Azzam Sheet Sync Summary",
        "",
        "| Target | Source CSV | Rows | Columns | Sheet ID |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in summary:
        lines.append(
            f"| {item['target']} | `{item['csv_path']}` | {item['written_rows']} | "
            f"{item['column_count']} | {item['sheet_id']} |"
        )
    lines.extend(
        [
            "",
            "Notes:",
            "- Rows count excludes the header row.",
            "- Payload uses Google Sheets `pasteData` requests starting at A1.",
            "- Review `sheet_sync_payload.json` before applying to a live workbook.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Google Sheets sync payload from local CSVs")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/sheets"))
    args = parser.parse_args()

    payload = build_sync_payload(resolve_default_targets(args.root))
    payload_path, summary_path = write_payload_files(payload, args.root / args.output_dir)
    print(f"wrote {payload_path}")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
