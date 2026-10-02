"""Validate generated CSVs for the Azzam YouTube data layer."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.youtube_data_layer import REMAKE_CANDIDATE_FIELDS, VIDEO_INVENTORY_FIELDS


def validate_csv(path: Path, required_fields: list[str], unique_field: str) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing file {path}"]

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        actual_fields = reader.fieldnames or []
        missing = [field for field in required_fields if field not in actual_fields]
        if missing:
            errors.append(f"missing columns in {path}: {', '.join(missing)}")
            return errors

        seen: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            value = (row.get(unique_field) or "").strip()
            if not value:
                errors.append(f"row {row_number}: blank {unique_field}")
                continue
            if value in seen:
                errors.append(f"duplicate {unique_field} {value}")
            seen.add(value)

    return errors


def validate_data_layer(data_dir: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_csv(data_dir / "video_inventory.csv", VIDEO_INVENTORY_FIELDS, "video_id"))
    errors.extend(validate_csv(data_dir / "remake_candidates.csv", REMAKE_CANDIDATE_FIELDS, "candidate_id"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Azzam YouTube data layer CSVs")
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    errors = validate_data_layer(args.data_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"validated {args.data_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
