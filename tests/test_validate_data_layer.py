import csv
import tempfile
import unittest
from pathlib import Path

from scripts.validate_data_layer import validate_csv
from scripts.youtube_data_layer import VIDEO_INVENTORY_FIELDS


class ValidateDataLayerTest(unittest.TestCase):
    def test_validate_csv_rejects_missing_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["video_id", "title"])
                writer.writeheader()
                writer.writerow({"video_id": "abc", "title": "Missing many columns"})

            errors = validate_csv(path, VIDEO_INVENTORY_FIELDS, unique_field="video_id")

        self.assertIn("missing columns", errors[0])

    def test_validate_csv_rejects_duplicate_unique_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dupes.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=VIDEO_INVENTORY_FIELDS)
                writer.writeheader()
                row = {field: "" for field in VIDEO_INVENTORY_FIELDS}
                row["video_id"] = "abc"
                writer.writerow(row)
                writer.writerow(row)

            errors = validate_csv(path, VIDEO_INVENTORY_FIELDS, unique_field="video_id")

        self.assertIn("duplicate video_id abc", errors)

    def test_validate_csv_accepts_valid_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=VIDEO_INVENTORY_FIELDS)
                writer.writeheader()
                row = {field: "" for field in VIDEO_INVENTORY_FIELDS}
                row["video_id"] = "abc"
                writer.writerow(row)

            errors = validate_csv(path, VIDEO_INVENTORY_FIELDS, unique_field="video_id")

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
