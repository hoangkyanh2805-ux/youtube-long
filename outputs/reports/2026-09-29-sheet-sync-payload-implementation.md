# Azzam Phase 1 Sheet Sync Payload Implementation

Date: 2026-09-29

## Completed

- Added payload builder: `scripts/sheet_sync_payload.py`.
- Added tests: `tests/test_sheet_sync_payload.py`.
- Generated:
  - `outputs/sheets/sheet_sync_payload.json`
  - `outputs/sheets/sheet_sync_summary.md`
- Added Google Sheet task `T-007`.
- Added dashboard metric `sync_001`.

## Payload Coverage

- `Video Inventory`: `data/processed/video_inventory.csv`, 100 rows, 22 columns.
- `Remake Candidates`: `data/processed/remake_candidates.csv`, 84 rows, 23 columns.
- `Shorts Pipeline`: `outputs/content/content_calendar.csv`, 10 rows, 27 columns.

## Notes

- The payload uses Google Sheets `pasteData` requests starting at A1.
- The local payload is auditable before live workbook writes.
- The current Google Drive connector call accepts structured request objects, not a local payload file path, so the JSON must be reviewed and applied by a caller that can load it into the connector request.

## Verification

- `python -m unittest tests.test_sheet_sync_payload`
- `python -m unittest discover`
- `python scripts\sheet_sync_payload.py --output-dir outputs\sheets`

## Remaining

- Add an adapter that can load `sheet_sync_payload.json` and pass it directly to the Google Sheets connector.
- Add bounded clear-range behavior before paste when a target table shrinks.
