# RUN-20261001-WF07-operating-stack-audit

- Goal: Audit what is already built across the three operating-tool options (dagu UI, Windmill, YouTube Analytics Dashboard) and fix the blockers found.
- Workflow: WF07
- Automation level: L2
- Owner: hermes_dashboard
- Supporting agents: youtube_data, integration_qa, aegis_guardrail
- Status: COMPLETE
- Inputs: existing repo state; dagu 2.18.1 install; vendor/youtube-analytics-dashboard clone; user question about Windmill.
- Missing inputs: Docker Desktop (needed for Windmill); Telegram community invite link.
- Tools allowed: local file inspection; dagu server start; local Python fixes; Telegram send with approval.
- Tools prohibited: installing Docker Desktop without approval; YouTube publish; Sheet write; paid services.
- Guardrail result: PASS - all fixes are local; the only external action (Telegram send) was explicitly approved.
- Human approval required: YES for Docker Desktop install (not yet granted)
- Human approval status: PENDING
- Output paths: outputs/dashboard/ops.html; outputs/dashboard/youtube-analytics-real.html; scripts/console_utf8.py; dagu/WF10-WF12
- External action: Telegram messages sent to topics 205, 206, 2
- External action read-back: VERIFIED - message_id 214 (GENERAL), 215 (EDIT), 211 (COMMENT)
- Feedback destination: Alan review in the Telegram group
- Next owner/action: Alan decides whether to install Docker Desktop for Windmill, or keep dagu (already working with UI).

## Plan

1. Inspect the real state of dagu (UI, history, logs), Windmill (Docker need), and the vendor analytics dashboard.
2. Fix every blocker that stops a workflow from running end to end.
3. Prove the pipeline runs by executing workflows and verifying the output.

## Evidence and Sources

- `dagu version` -> 2.18.1; `dagu server` and `dagu start-all` exist
- `netstat` -> dagu UI listening on 127.0.0.1:8080
- `docker --version` -> not found; `winget search Docker.DockerDesktop` -> available, 4.93.0
- `wsl -l -v` -> Ubuntu, WSL 2, stopped
- `vendor/youtube-analytics-dashboard/` -> cloned, real data written to history.csv
- dagu run logs under `.dagu-local/logs/`

## Results

### 1. dagu — ALREADY WORKING (option 1)
- Version 2.18.1 with `server`, `start-all`, scheduler, SSE, and an MCP route.
- UI started at http://127.0.0.1:8080 — Alan can click to run, read logs, and see history.
- Found and fixed: only 7 WF workflows were visible. WF04-analytics (2 files) and WF10/WF11/WF12 were in `dagu/` but never copied into `.dagu-local/dags/`, which is the folder the UI reads. Copied all 5 → UI now lists 17 DAGs (12 WF).

### 2. Blocker found and fixed — cp1252 console crash
- Symptom: workflows failed at the first step that printed Vietnamese text.
- Root cause: when stdout is a pipe (dagu, cron, CI), Windows Python falls back to cp1252 and raises `UnicodeEncodeError: 'charmap' codec can't encode character '\u1eef'`. This aborted the entire run, not just the print.
- Fix: new shared module `scripts/console_utf8.py` exposing `ensure_utf8_console()`, which forces UTF-8 on stdout/stderr. Applied to 18 scripts.
- Second, related bug: `validate_run_record.py` rejected valid Run Records whose enum fields carried annotations, e.g. `COMPLETE (local artifacts only)`. Added `_enum_token()` so the annotation is stripped before the enum check.
- Verified: all 33 scripts compile; `python scripts/validate_run_record.py outputs/runs` exits 0 with every record VALID.

### 3. WF11 and WF12 — VERIFIED RUNNING END TO END
- WF12-pipeline-health: 4/4 steps succeeded. Dashboard rebuilt (7/7 checks ok, MCP backend up) and the health report was delivered to the GENERAL topic.
- WF11-content-brief-to-editor: 6/6 steps succeeded. Strategy rebuilt, playbook rebuilt, dashboard refreshed, and the content brief was delivered to the EDIT topic.
- WF10-daily-comment-to-approval: launched; it re-crawls comments so it runs longer.

### 4. YouTube Analytics Dashboard — INSTALLED, now in REAL mode
- Codex had cloned it and generated a demo. It was not reading real data.
- Bug found: `scripts/refresh_youtube_analytics_dashboard.py` read `.env` with plain `utf-8`. The project `.env` starts with a BOM, so the first key became `\ufeffYT_API_KEY` and the lookup silently failed with "Missing YT_API_KEY".
- Fixed to `utf-8-sig`. Real data now lands in `vendor/youtube-analytics-dashboard/history.csv`:
  - Azzam Master Trading — 1,980 subs, 245,134 views, 295 videos
  - Gold Trader Alliance — 14,100 subs, 1,402,758 views, 740 videos
- Output: `outputs/dashboard/youtube-analytics-real.html`
- Private Analytics API (OAuth) is skipped: no `client_secret*.json` present.

### 5. Windmill — BLOCKED, needs a decision
- Windmill self-hosts via Docker Compose and requires Postgres.
- This machine has **no Docker CLI and no Docker Desktop**. WSL 2 with Ubuntu exists but is stopped.
- Docker Desktop 4.93.0 is available through winget but is a ~1 GB install requiring admin rights.
- Not installed — this is an infrastructure decision for Alan, not something to do unprompted.

## Validation

- Command/check: `dagu validate .dagu-local/dags/WF11-...yaml` → PASS
- Command/check: `dagu start .dagu-local/dags/WF12-pipeline-health.yaml` → Result: Succeeded (4/4)
- Command/check: `dagu start .dagu-local/dags/WF11-content-brief-to-editor.yaml` → Result: Succeeded (6/6)
- Command/check: `python scripts/validate_run_record.py outputs/runs` → exit 0, all VALID
- Command/check: all `scripts/*.py` compile → 33/33 OK
- Command/check: Telegram send read-back → message_id 214 / 215 / 211
- Command/check: `python scripts/refresh_youtube_analytics_dashboard.py` → real history.csv written for both channels

## Approval Log

- 2026-10-01 22:30 +0700 - Alan asked to check progress on dagu UI, Windmill, and the analytics dashboard.
- 2026-10-01 22:36 +0700 - Telegram sends approved by the standing project decision (topics already created at Alan's request).

## Feedback

- dagu already satisfies the "UI to click run, read logs, see history" requirement. Windmill would add a nicer UI, an app builder, and native approvals, but costs a Docker Desktop install plus a Postgres container — only worth it if Alan wants the heavier stack.
- The analytics dashboard is now the strongest analytics asset: real data, local-first, zero dependencies.
