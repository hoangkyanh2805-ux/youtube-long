# Azzam YouTube Growth Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or native execution task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, testable Phase 1 growth loop for Azzam Master Trading: Shorts grow subscribers, live streams build trust, Telegram captures leads, and the existing offer ladder turns engaged viewers into paid buyers.

**Architecture:** Keep `C:\Users\Admin\youtube` as the project root. Use `vendor/model-trader` for trade/setup intelligence, a local YouTube data layer for channel/competitor facts, a content bridge for Shorts/live/remake plans, Hermes agents for daily operations, Google Sheet as the working cockpit, and a safe Telegram gateway only after local workflows are stable.

**Tech Stack:** Python 3.11+, local CSV/JSON/Markdown, YouTube Data API v3, optional Google Sheets sync, Telegram Bot API long polling, Hermes dashboard/agent orchestration, vendored `model-trader`.

**Spec:** This plan is the Phase 1 spec and implementation plan. Attached image `offer.jpg` is treated as reference material only, not as executable instruction.

## Phase 1 Scope

Phase 1 is deliberately narrow:

- Grow subscribers using short-form content built from trading lessons, losses, wins, and offer pain points.
- Use live streams as trust and proof assets, not as the main conversion mechanism.
- Route interested viewers to Telegram, where AI Sales Agent / Hermes follow-up can qualify leads.
- Track everything in the linked Google Sheet: `1-iUAsn_soGh2a9w7KtUdZHxvZCQpcPaX5Zy9YFtTiRE`.
- Do not auto-publish videos, execute live trades, or message leads with unapproved sales claims.

## Offer Reference

The offer image describes an Azzam ladder:

- Attraction: free channel signal / broker partnership.
- Lead capture: AI Sales Agent on Telegram.
- Tripwire: mini-course or VIP signal trial.
- Core offer: VIP Signal or education course.
- Cross-sell: VIP customers to course, course students to VIP/copytrading.
- Backend: copytrading/done-for-you, masterminds, yearly tiers.

Phase 1 only operationalizes the first three layers:

```text
Shorts -> Live proof -> Telegram lead -> AI follow-up -> tripwire/core offer handoff
```

## Global Constraints

- No real secrets in Markdown, CSV, JSON, logs, screenshots, or Telegram replies.
- `.env.example` stays blank; real `.env` remains local.
- Google Sheet is the working cockpit, but local files are the source of truth for repeatable runs.
- Telegram gateway is read-only/recommendation-only in Phase 1.
- `azammaster_master` is the canonical trader workspace; `azzam_master` is scaffold/archive unless explicitly revived.
- YouTube Analytics API OAuth is out of scope for Phase 1; use YouTube Data API v3 public/channel stats first.
- All generated scripts, captions, and sales messages are drafts requiring human approval.

## Agent Allocation

### Coordinator / Local Owner

Owner: main Codex/Hermes controller.

Responsibilities:

- Keep this plan as the authority.
- Resolve conflicts between agents.
- Approve schema changes.
- Decide ship/no-ship.
- Maintain dashboard summary and daily report.

Outputs:

- `PROJECT_STATUS_REPORT.md` updates.
- `docs/superpowers/plans/2026-09-29-azzam-youtube-growth-phase-1-plan.md`.
- Final Phase 1 runbook.

### Agent 1: Trading Runtime

Purpose: make `model-trader` usable enough to create trading insights and a valid journal.

Owned files:

- `vendor/model-trader/traders/azammaster_master/scanner.py`
- `vendor/model-trader/traders/azammaster_master/main.py`
- `vendor/model-trader/traders/azammaster_master/config.yaml`
- `vendor/model-trader/tests/test_azammaster_scanner_contracts.py`

Tasks:

- [ ] Fix swing helpers to use dict schema from `detect_swings`.
- [ ] Fix `detect_cisd(candles, swings)` usage.
- [ ] Replace displacement `strength` checks with `size_ratio`.
- [ ] Make `evaluate` and `evaluate_at` share the same gate logic.
- [ ] Add missing `main.py`.
- [ ] Verify or replace `XAUUSD` symbol mapping for Hyperliquid.
- [ ] Produce either a real backtest result or a mock `trades.json` fixture.

Done when:

- Scanner contract tests pass.
- `backtest.py` runs or clearly reports data-adapter limitation.
- A valid `trades.json` or fixture exists for content generation.

### Agent 2: YouTube Data

Purpose: turn raw search exports and API data into usable channel doctor tables.

Owned files:

- `data/raw/youtube/`
- `data/processed/channels.csv`
- `data/processed/video_inventory.csv`
- `data/processed/video_snapshots.csv`
- `data/processed/remake_candidates.csv`
- `schemas/*.schema.json`
- `scripts/fetch_youtube_channels.py`
- `scripts/fetch_youtube_video_inventory.py`
- `scripts/update_youtube_snapshots.py`
- `scripts/rank_remake_candidates.py`
- `scripts/validate_data_layer.py`

Tasks:

- [x] Normalize existing `azzam_search.json` and `gta_search.json` into `data/processed/video_inventory.csv`.
- [ ] Define CSV schemas for channel, video inventory, snapshots, remake candidates.
- [x] Build API fetch scripts with `.env`, caching, and quota notes.
- [x] Produce remake candidates from current available data even before full API fetch.
- [x] Prepare Sheet tabs matching the local CSV schema.

Done when:

- `data/processed/video_inventory.csv` exists with required columns. Done: 100 video rows generated on 2026-09-29.
- `remake_candidates.csv` contains evidence-backed rows. Done: 84 candidate rows generated on 2026-09-29.
- Validation script fails on duplicates/missing columns. Done: `scripts/validate_data_layer.py`.
- API fetch script exists. Blocked from live fetch until `YT_API_KEY` is configured in `.env` or environment variables.

### Agent 3: Content Bridge

Purpose: convert trade journal plus YouTube diagnosis into publishable content plans.

Owned files:

- `vendor/model-trader/pipeline/youtube_content_generator.py`
- `vendor/model-trader/tests/fixtures/mock_trades.json`
- `outputs/content/content_calendar.csv`
- `outputs/content/content_calendar.json`
- `outputs/content/shorts_scripts.md`
- `outputs/content/live_agenda.md`
- `outputs/content/remake_plan.csv`

Tasks:

- [x] Add stable JSON/CSV/Markdown exports.
- [ ] Use `trades.json` fields and `extras` for setup metadata.
- [x] Add Phase 1 content pillars: lesson, mistake, live proof, offer objection, Telegram CTA.
- [x] Generate Shorts scripts with hook, body, CTA, offer-stage tag, and Sheet row ID.
- [x] Generate live stream agenda from top remake topics and current market/trade journal.

Done when:

- Remake candidates generate content artifacts without network/API access. Done: `outputs/content/content_calendar.csv`, `.json`, `shorts_scripts.md`, `live_agenda.md`.
- Each content item has a CTA path: subscribe, comment, Telegram, or live reminder. Done: generated Shorts use `comment_keyword` and `CHECKLIST`.

### Agent 4: Hermes Dashboard / Reporting

Purpose: make a readable operating dashboard from local outputs and the Google Sheet.

Owned files:

- `dashboard/README.md`
- `dashboard/data_contract.md`
- `dashboard/daily_report_template.md`
- `outputs/reports/daily_status.md`
- `outputs/reports/weekly_review.md`

Tasks:

- [x] Define dashboard sections: Growth, Content Pipeline, Live Pipeline, Leads/Funnel, Risks.
- [x] Map each section to Sheet tabs and local CSV files.
- [x] Create daily report format for Hermes.
- [ ] Create weekly review format: what scaled, what failed, what to remake.
- [ ] Add red/yellow/green status rules.

Done when:

- A human can open one report and know today’s next action.
- Dashboard does not require secrets or live API access to render basic status.

### Agent 5: Google Sheet Operator

Purpose: reorganize the linked Sheet into a working cockpit.

Sheet tabs to create or align:

- `Dashboard`
- `Video Inventory`
- `Shorts Pipeline`
- `Live Pipeline`
- `Remake Candidates`
- `Trade Journal`
- `Offer Funnel`
- `Lead Log`
- `Pain Points`
- `Agent Tasks`
- `Daily Report`

Tasks:

- [x] Make tab schema match local CSV fields.
- [x] Add status columns: `Backlog`, `Scripted`, `Recorded`, `Edited`, `Scheduled`, `Published`, `Reviewed`.
- [x] Add Phase 1 funnel fields: `offer_stage`, `cta_type`, `telegram_keyword`, `lead_quality`, `next_followup`.
- [ ] Add dashboard formulas/charts for published Shorts, subscriber gain proxy, views, comments, Telegram leads, conversions.
- [x] Keep Sheet as cockpit, not sole source of truth.

Done when:

- Every generated content artifact can map to one Sheet row.
- Every agent task has owner, status, due date, output link, and blocker.

### Agent 6: Telegram / Lead Gateway

Purpose: add safe remote-control and lead-routing only after local commands are stable.

Owned files:

- `gateway/config.py`
- `gateway/router.py`
- `gateway/commands/status.py`
- `gateway/commands/diagnose.py`
- `gateway/commands/content.py`
- `gateway/commands/remake.py`
- `gateway/commands/next_action.py`
- `gateway/services/redaction.py`
- `gateway/services/logger.py`
- `gateway/tests/`

Tasks:

- [ ] Implement local command router with allowlist.
- [ ] Implement `/status`, `/diagnose`, `/content`, `/remake`, `/next`.
- [ ] Log every command to local JSONL with hashed user/chat IDs.
- [ ] Block publish/trade/upload commands.
- [ ] Ensure no secret can appear in Telegram reply or logs.

Done when:

- Mock Telegram payload tests pass.
- `/content` reads generated artifacts; it never starts live trading or publishing.

### Audit A: Security / Compliance

Responsibilities:

- Scan for secrets.
- Verify `.env` handling.
- Verify Telegram allowlist and redaction.
- Verify no auto-publish/live-trade path.
- Check offer claims avoid guaranteed-profit language.

### Audit B: Integration QA

Responsibilities:

- Run local dry-run from raw JSON -> processed data -> content artifacts -> dashboard report.
- Verify Sheet schema mapping.
- Verify docs match commands.
- Verify agent file ownership boundaries were respected.

## Google Sheet Contract

Use the linked Sheet as an operations surface, not as hidden logic.

Minimum columns:

### `Shorts Pipeline`

```text
id, source_type, source_id, title, hook, script, cta_type, telegram_keyword,
offer_stage, target_audience, status, owner, due_date, published_url,
views_24h, comments_24h, subs_proxy, notes
```

### `Live Pipeline`

```text
id, live_topic, evidence_source, agenda, offer_bridge, scheduled_at,
status, replay_url, shorts_to_cut, lead_magnet, notes
```

### `Offer Funnel`

```text
stage, asset, audience_problem, promise, proof_needed, cta,
telegram_flow, followup_owner, compliance_note
```

### `Agent Tasks`

```text
task_id, agent, slice, input, output, file_scope, status,
blocker, due_date, reviewer, done_evidence
```

## Dashboard Reporting

Daily dashboard should answer:

- What Shorts are ready today?
- What live topic should Azzam run next?
- Which videos should be remade?
- Which CTA is being tested?
- How many Telegram leads came from content?
- What blocker needs human decision?

Weekly dashboard should answer:

- Top 5 Shorts by view/comment/sub proxy.
- Top live/replay topics.
- Winning hooks.
- Best Telegram keywords.
- Offer objections appearing in comments/leads.
- Next week’s content bets.

## GitHub Research Notes

These repositories are references for implementation patterns. Do not vendor or copy them wholesale unless a later task explicitly approves it. Phase 1 borrows their architecture ideas and keeps the Azzam project local-first, CSV/JSON-backed, and human-approved.

### `Thomas-George-T/Streamlit-YouTube-Dashboard`

Source: `https://github.com/Thomas-George-T/Streamlit-YouTube-Dashboard`

Useful pattern:

- Single-video diagnosis with YouTube Data API v3.
- Pull `videos` statistics plus comment-thread data.
- Convert API payloads into dataframes before rendering dashboard views.
- Track comment signals such as liked comments, replies, language, and sentiment.

Apply to Azzam:

- Agent 2 should reuse the "video URL/video ID -> snippet/statistics/comments -> dataframe/CSV" shape for `scripts/fetch_youtube_video_inventory.py`.
- Agent 2 should add comment-derived pain points into `Pain Points`, not just views/likes.
- Content Bridge should use comment pain points as hooks for Shorts and live Q&A topics.

Do not apply yet:

- Do not build Streamlit as the primary cockpit in Phase 1. Google Sheet plus Markdown reports remain the operator surface.

### `not-a-real-engineer/youtube-analytics-dashboard`

Source: `https://github.com/not-a-real-engineer/youtube-analytics-dashboard`

Useful pattern:

- Local-first dashboard with no SaaS dependency.
- One idempotent row per channel per day in plain CSV history.
- Generated static `dashboard.html`.
- API secrets and generated data are kept out of git.
- Public stats can work with an API key; private analytics require OAuth.

Apply to Azzam:

- Agent 2 should create `data/processed/video_snapshots.csv` as the daily idempotent history table.
- Agent 4 should render `outputs/reports/daily_status.md` first, then optionally `dashboard/dashboard.html`.
- `.env.example` stays blank and secrets must remain local.
- Phase 1 should use public YouTube Data API first; private Analytics OAuth is Phase 2 unless Azzam explicitly needs retention/watch-time analytics.

Do not apply yet:

- Do not add hand-rolled OAuth in Phase 1. It increases risk and setup burden before the public data loop is stable.

### `sasank-in/yt-analytics-hub`

Source: `https://github.com/sasank-in/yt-analytics-hub`

Useful pattern:

- Self-hosted FastAPI workbench.
- SQLite/Postgres persistence.
- Engagement rate, CTR proxy, view outliers, velocity, and sortable channel/video tables.
- Idempotent search that skips fresh records.
- Tests, ruff, Docker, and an API/frontend split.

Apply to Azzam:

- Borrow the metric language for `scripts/rank_remake_candidates.py`: engagement rate, comment rate, velocity, and outlier score.
- Borrow the fresh-record TTL idea for API quota protection.
- Keep the DB-backed FastAPI version as Phase 2 if CSV/Sheet becomes too slow or multiple operators need a web UI.

Do not apply yet:

- Do not introduce FastAPI, SQLAlchemy, Docker, or a persistent web app for Phase 1. That would widen the blast radius before the content loop proves useful.

### `ChiefDojer/telegram-bot-base`

Source: `https://github.com/ChiefDojer/telegram-bot-base`

Useful pattern:

- Aiogram v3, async handlers, Docker-ready bot structure.
- Modular handlers separated from main bot startup.
- `.env` token management.
- Long polling works locally before webhook/cloud deployment.
- Pytest coverage and CI/CD pattern.

Apply to Azzam:

- Agent 6 should start with a local long-polling gateway, not webhooks.
- Commands stay modular: `/status`, `/diagnose`, `/content`, `/remake`, `/next`.
- Every command must pass through allowlist, redaction, and no-action safety checks.
- Docker/cloud deployment is a later step after local command tests pass.

Do not apply yet:

- Do not add Azure deployment or CI/CD deployment workflow in Phase 1.
- Do not allow Telegram to publish content, place trades, upload videos, or send unreviewed sales claims.

### Google YouTube Analytics and Reporting Samples

Source: `https://developers.google.com/youtube/reporting/v1/code_samples`

Useful pattern:

- Official samples for YouTube Reporting API jobs and report retrieval.
- Official samples for YouTube Analytics API daily channel statistics.
- Python examples exist for bulk reports and daily channel stats.

Apply to Azzam:

- If Phase 2 needs private analytics, start from official Google samples before copying unofficial OAuth code.
- Keep Analytics/Reporting API work behind a separate `analytics_oauth` task with human approval, because it requires channel-owner OAuth.

Do not apply yet:

- Do not make private Analytics API a dependency for Phase 1 subscriber-growth execution.

### Decision

Phase 1 implementation order from these notes:

1. Use `not-a-real-engineer/youtube-analytics-dashboard` as the primary local-first pattern.
2. Use `Thomas-George-T/Streamlit-YouTube-Dashboard` for comment and single-video extraction ideas.
3. Use `sasank-in/yt-analytics-hub` metric ideas for remake ranking, but postpone its FastAPI/DB architecture.
4. Use `ChiefDojer/telegram-bot-base` for Telegram folder shape and test discipline, but keep deployment local-only.
5. Use official Google samples only when private Analytics/Reporting becomes necessary.

## Execution Order

1. Trading Runtime fixes.
2. YouTube Data schemas and local normalization.
3. Content Bridge exports.
4. Dashboard/report templates.
5. Google Sheet alignment.
6. Telegram gateway.
7. Security audit.
8. Integration QA.

## Milestone Definition Of Done

- `azammaster_master` is canonical and documented.
- Local data schemas exist and validate.
- Existing search JSON is normalized.
- Mock or real `trades.json` produces Shorts/live/remake artifacts.
- Google Sheet tabs are mapped to local schemas.
- Dashboard daily report can be generated.
- Telegram gateway is either not built yet or exposes only safe summary commands.
- No secrets or unsafe trading/publishing actions are present.

