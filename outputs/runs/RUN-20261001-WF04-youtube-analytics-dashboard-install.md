# RUN-20261001-WF04-youtube-analytics-dashboard-install

- Goal: Clone and run the not-a-real-engineer YouTube Analytics Dashboard as a local analytics dashboard reference.
- Workflow: WF04
- Automation level: L2
- Owner: hermes_dashboard
- Supporting agents: youtube_data, integration_qa, aegis_guardrail
- Status: COMPLETE
- Inputs: https://github.com/not-a-real-engineer/youtube-analytics-dashboard; user request; existing local dashboard output folder.
- Missing inputs: NONE for demo mode; real API mode still needs safe API/OAuth setup.
- Tools allowed: git clone; local Python standard-library demo render; local file copy; Dagu workflow wrapper.
- Tools prohibited: YouTube API calls with real credentials; OAuth private analytics; Google Sheet write; Telegram send; YouTube publish.
- Guardrail result: PASS - demo uses fictional sample data only and no external API call.
- Human approval required: NO - local clone and demo render only.
- Human approval status: NOT_REQUIRED
- Output paths: vendor/youtube-analytics-dashboard; outputs/dashboard/youtube-analytics-demo.html; dagu/WF04-youtube-analytics-dashboard-demo.yaml
- External action: NONE
- External action read-back: NOT_REQUIRED
- Feedback destination: Hermes Dashboard and Founder Memory after Alan review
- Next owner/action: Alan opens outputs/dashboard/youtube-analytics-demo.html; if approved, next task maps real local CSV/API data into the vendor dashboard or launches serve.py for manual API-key refresh.

## Plan

1. Clone the upstream dashboard repo into `vendor/`.
2. Run its built-in demo without API keys.
3. Copy the generated HTML into project dashboard outputs.
4. Add a Dagu workflow to rebuild the demo.

## Evidence and Sources

- `vendor/youtube-analytics-dashboard/README.md`
- `vendor/youtube-analytics-dashboard/build_dashboard.py`
- `vendor/youtube-analytics-dashboard/sample_data/`

## Results

- Vendor repo cloned.
- Demo dashboard generated successfully.
- Project output created at `outputs/dashboard/youtube-analytics-demo.html`.
- Dagu wrapper added as `WF04-youtube-analytics-dashboard-demo`.

## Validation

- Command/check: `$env:PYTHONUTF8='1'; python build_dashboard.py --demo`
- Result: `Wrote dashboard.html (demo) - 35 history rows, analytics OK, comments OK`
- Command/check: `python scripts\validate_run_record.py outputs\runs`
- Result: PASS - 5 run records valid.
- Command/check: `dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local validate dagu\WF04-youtube-analytics-dashboard-demo.yaml`
- Result: PASS.
- Command/check: `dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local start dagu\WF04-youtube-analytics-dashboard-demo.yaml`
- Result: PASS - workflow succeeded and rebuilt `outputs/dashboard/youtube-analytics-demo.html`.

## Approval Log

- 2026-10-01 19:20 +0700 - Alan requested installing the YouTube Analytics Dashboard repo.

## Feedback

- The dashboard is installed and runs in demo mode. Real mode needs a separate L3/L2-safe credentials decision before touching Google APIs.
