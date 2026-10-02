# RUN-20261001-WF04-youtube-analytics-api-connect

- Goal: Connect the cloned YouTube Analytics Dashboard to real YouTube Data API data and prepare private OAuth analytics.
- Workflow: WF04
- Automation level: L3
- Owner: hermes_dashboard
- Supporting agents: youtube_data, integration_qa, aegis_guardrail
- Status: RUNNING
- Inputs: user approval to connect; root `.env` with `YT_API_KEY`; channel IDs from `agents/youtube_data/config.yaml`; cloned vendor dashboard.
- Missing inputs: `vendor/youtube-analytics-dashboard/client_secret*.json` for private YouTube Analytics OAuth.
- Tools allowed: local credential presence checks; read-only YouTube Data API calls; local OAuth flow when `client_secret*.json` exists; local dashboard generation; Dagu workflow wrapper.
- Tools prohibited: Google Sheet write; Telegram send; YouTube upload/publish; credential printing; paid quota expansion.
- Guardrail result: PASS - read-only API refresh only; secrets are not printed.
- Human approval required: YES
- Human approval status: APPROVED
- Output paths: vendor/youtube-analytics-dashboard/channels.json; vendor/youtube-analytics-dashboard/history.csv; vendor/youtube-analytics-dashboard/comments.json; vendor/youtube-analytics-dashboard/analytics_latest.json; outputs/dashboard/youtube-analytics-real.html; dagu/WF04-youtube-analytics-dashboard-real.yaml
- External action: READ_ONLY_GOOGLE_YOUTUBE_APIS
- External action read-back: PENDING
- Feedback destination: Hermes Dashboard and Founder Memory after Alan review
- Next owner/action: Codex runs public API refresh; Alan provides OAuth desktop `client_secret*.json` if private owner analytics is required.

## Plan

1. Configure `channels.json` from project source-of-truth channel IDs.
2. Load `YT_API_KEY` from root `.env` without printing it.
3. Pull public channel stats and comments through YouTube Data API v3.
4. Run private YouTube Analytics OAuth only if `client_secret*.json` exists.
5. Build and copy the real dashboard output.

## Evidence

- `agents/youtube_data/config.yaml`
- `vendor/youtube-analytics-dashboard/README.md`
- `scripts/refresh_youtube_analytics_dashboard.py`
- `dagu/WF04-youtube-analytics-dashboard-real.yaml`

## Validation

- Pending final run.

## Approval Log

- 2026-10-01 - Alan requested connecting Google OAuth / YouTube Analytics API fully.

## Feedback

- Public API can run with existing `YT_API_KEY`.
- Private YouTube Analytics OAuth is blocked until a Google Cloud OAuth Desktop client secret file is placed in the vendor dashboard folder.
