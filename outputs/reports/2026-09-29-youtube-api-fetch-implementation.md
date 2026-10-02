# Azzam YouTube API Fetch Implementation

Date: 2026-09-29

## What Is Done

- Added YouTube Data API fetcher: `scripts/youtube_api_fetch.py`.
- Added tests: `tests/test_youtube_api_fetch.py`.
- The fetcher reads `YT_API_KEY`, `YOUTUBE_CHANNEL_ID`, and `COMPETITOR_CHANNEL_ID` from `.env` or environment variables.
- The fetcher can produce:
  - `data/processed/video_inventory_api.csv`
  - `data/processed/video_snapshots.csv`
  - `data/processed/channels.csv`

## Current Blocker

The workspace does not contain a real `.env` file and the environment does not expose `YT_API_KEY`.

The command:

```powershell
python scripts\youtube_api_fetch.py --root . --check-key-only
```

currently fails with:

```text
Missing YT_API_KEY. Put the real key in .env or environment variable.
```

## Exact Next Step

Create `C:\Users\Admin\youtube\.env` locally with:

```dotenv
YT_API_KEY=PASTE_REAL_YOUTUBE_DATA_API_KEY_HERE
YOUTUBE_CHANNEL_ID=UCBZ7LaffmEPv91sWcfroJdQ
COMPETITOR_CHANNEL_ID=UCdS8VXFlNvVohM09qzZGCkA
```

Then run:

```powershell
python scripts\youtube_api_fetch.py --root . --check-key-only
python scripts\youtube_api_fetch.py --root . --date 2026-09-29
python scripts\validate_data_layer.py --data-dir data\processed
```

## Verification Already Run

- `python -m unittest tests.test_youtube_api_fetch`
- `python -m unittest discover`
- `python scripts\youtube_api_fetch.py --root . --check-key-only`

The tests pass. The key check fails because the real API key is not configured.

## Sources

- Official YouTube Data API `videos.list`: https://developers.google.com/youtube/v3/docs/videos/list
- Official YouTube Data API `channels.list`: https://developers.google.com/youtube/v3/docs/channels/list
