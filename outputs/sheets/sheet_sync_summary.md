# Azzam Sheet Sync Summary

| Target | Source CSV | Rows | Columns | Sheet ID |
| --- | --- | ---: | ---: | ---: |
| Video Inventory | `data\processed\video_inventory_api.csv` | 100 | 22 | 1006 |
| Remake Candidates | `data\processed\remake_candidates_api.csv` | 50 | 23 | 1005 |
| Shorts Pipeline | `outputs\content\content_calendar.csv` | 10 | 27 | 1003 |

Notes:
- Rows count excludes the header row.
- Payload uses Google Sheets `pasteData` requests starting at A1.
- Review `sheet_sync_payload.json` before applying to a live workbook.