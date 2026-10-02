# GitHub Skill Pack -> Azzam Phase 1 Agent Map

Date: 2026-09-29

Purpose: map five external skill repositories into the Azzam Phase 1 operating system without blindly installing or copying them. The target outcome is still:

```text
Shorts grow subscribers -> Live builds trust -> Telegram captures leads -> Offer converts
```

## Source Inventory

| Source | Verified URL | Role | Confidence | Notes |
|---|---|---|---|---|
| tutor-skills | https://github.com/bevibing/tutor-skills | tutor / learning workflow | High | Verified via skills.sh page. Core pattern: quiz-based tutor + StudyVault dashboard/concept files. |
| youtube-skills | https://github.com/ZeroPointRepo/youtube-skills | YouTube workflow toolkit | High | Verified README. Skills include transcripts, search, channels, playlists, youtube-data/API variants. |
| platform-design-skills | https://github.com/ehmo/platform-design-skills | platform-specific UI guidance | Medium | Verified skills.sh listing. Includes macOS, iOS, Android, web, iPadOS, watchOS, tvOS, visionOS guidelines. |
| Aegis | https://github.com/GanyuanRan/Aegis | guardrail / architecture-aware agent safety | High | Verified README. Pattern: baseline-first, evidence-verified, drift-checked, architecture-aware agent work. |
| founder-skills | https://github.com/ognjengt/founder-skills | founder operations | Medium | User source. Public listing describes packaged startup workflows, but GitHub details were less directly visible. |
| founder-skills alternative | https://github.com/gvkhosla/founder-skills | founder operations | High | Verified README. Pattern: choose direction, validate, scope, plan, launch, review signals, update memory. |

## Extracted Mechanisms

| Source | Mechanism | Reusable Principle | Azzam Use |
|---|---|---|---|
| tutor-skills | StudyVault with compact dashboard and per-concept files | Track what the learner knows, not just publish content | Turn Azzam education content into mini lessons, quizzes, and learning gaps for lead nurturing. |
| youtube-skills | Transcript/search/channel/playlist skills | A YouTube agent should pull the actual content layer, not only public stats | Add transcript mining and competitor topic extraction before script generation. |
| platform-design-skills | Platform-specific design guidelines | Interface should fit the surface: Sheet, web dashboard, Telegram, mobile | Make Hermes Dashboard dense and scannable; Telegram concise; Sheet operational. |
| Aegis | Baseline-first, evidence-verified, drift-checked | Agents must prove state before acting, and detect drift after long tasks | Add preflight/read-back checks before Sheet sync, API fetch, content output, Telegram sending. |
| founder-skills | Founder loop: choose, validate, scope, launch, review, update memory | Startup work compounds through saved artifacts and weekly decisions | Add Founder Ops Agent to decide the highest-leverage weekly move, offer experiment, and conversion hypothesis. |

## Target Project Map

### Already Exists

- YouTube public API fetch: `scripts/youtube_api_fetch.py`
- API-ranked remake candidates: `scripts/rank_remake_candidates.py`
- Content drafts: `scripts/content_bridge.py`
- Daily report renderer: `scripts/daily_report_renderer.py`
- Sheet sync payload: `scripts/sheet_sync_payload.py`
- Live Google Sheet: `Azzam Phase 1 Growth Cockpit`
- Agent folders: `agents/youtube_data`, `agents/content_bridge`, `agents/hermes_dashboard`, `agents/google_sheet_operator`, `agents/telegram_gateway`

### New Agent Roles To Add

1. `Learning Tutor Agent`
   - Source pattern: tutor-skills
   - Mission: convert Azzam educational content and offer materials into lesson cards, quiz prompts, and concept gaps.
   - Output: `outputs/learning/study_vault/dashboard.md`, `outputs/learning/study_vault/concepts/*.md`

2. `YouTube Workflow Agent`
   - Source pattern: youtube-skills
   - Mission: enrich the current Data + Content Bridge pipeline with transcript/topic extraction and competitor content mining.
   - Output: `data/processed/transcript_topics.csv`, `outputs/content/topic_briefs.md`

3. `Platform UX Agent`
   - Source pattern: platform-design-skills
   - Mission: make each interface fit its platform: Google Sheet as control room, Markdown as daily report, Telegram as command channel, web dashboard as scan view.
   - Output: `docs/platform-ux-rules.md`, dashboard/sheet/telegram UI checklists.

4. `Aegis Guardrail Auditor`
   - Source pattern: Aegis
   - Mission: run baseline, evidence, drift, secret, and compliance checks before any external write/publish/send step.
   - Output: `outputs/audit/aegis_guardrail_report.md`

5. `Founder Ops Agent`
   - Source pattern: founder-skills
   - Mission: turn raw metrics and offer context into one weekly founder decision: what to do next, what to validate, what to stop.
   - Output: `outputs/founder/weekly_founder_brief.md`, `knowledge/distilled/founder-context.md`

## Agent Contract Table

| Agent | Receives | Produces | Not Responsible For | Metrics |
|---|---|---|---|---|
| Learning Tutor Agent | Offer ladder, scripts, live notes, audience pain points | Quiz cards, concept gap files, Telegram nurture lesson snippets | Trading advice, publishing, sales closing | Lessons created, concepts tracked, quiz completion proxy |
| YouTube Workflow Agent | YouTube API inventory, candidate list, transcript/source URLs | Transcript topics, hook library, competitor topic briefs | Publishing, Analytics OAuth, paid scraping by default | Topics extracted, transcript coverage, candidate quality |
| Platform UX Agent | Dashboard/report/sheet/Telegram surfaces | UI rules and review notes per platform | Backend logic, API fetches, design that hides risk | Readability, no clipping, no confusing workflow labels |
| Aegis Guardrail Auditor | Diff, outputs, Sheet ranges, env/secrets, report state | Pass/fail audit and drift notes | Creating content, changing strategy | Zero leaked secrets, read-back success, no unapproved external action |
| Founder Ops Agent | Daily report, dashboard metrics, offer funnel, lead log | Weekly verdict, next move, validation hypothesis | Writing code, sending offers, changing pricing without approval | One clear weekly move, tracked assumption, decision log updated |

## Harness Loop Map

```text
daily_api_snapshot
  -> aegis_preflight_check
  -> youtube_workflow_enrichment
  -> rank_remake_candidates
  -> content_bridge_drafts
  -> learning_tutor_pack
  -> platform_ux_review
  -> hermes_daily_report
  -> google_sheet_sync
  -> aegis_readback_and_drift_check
  -> founder_ops_weekly_review_if_due
```

## State Schema

```json
{
  "workflow_id": "azzam_phase1_daily_loop",
  "snapshot_date": "YYYY-MM-DD",
  "channel_snapshot_available": false,
  "api_inventory_path": "data/processed/video_inventory_api.csv",
  "top_candidate_id": "",
  "top_short_id": "",
  "learning_pack_status": "pending",
  "sheet_sync_status": "pending",
  "aegis_status": "pending",
  "founder_decision_status": "not_due",
  "needs_human": false,
  "human_gate_reason": "",
  "errors": [],
  "last_checkpoint": ""
}
```

## Tool And Permission Matrix

| Action | Autonomous | Human Approval Required | Forbidden |
|---|---:|---:|---:|
| Read public GitHub docs/repos | Yes | No | No |
| Install third-party skills globally | No | Yes | No |
| Fetch public YouTube Data API stats | Yes | No, if `.env` exists | No |
| Fetch private YouTube Analytics OAuth data | No | Yes | No |
| Generate draft scripts/lessons | Yes | No | No |
| Publish YouTube videos/Shorts | No | Yes | Auto-publish forbidden |
| Send Telegram broadcasts/offers | No | Yes | Mass send without approval forbidden |
| Change offer/pricing | No | Yes | No |
| Execute trades | No | No | Forbidden |
| Write Google Sheet ops rows | Yes | No, if scoped/read-back verified | No destructive rewrite without approval |

## Guardrails

| Risk | Guardrail | Stop Condition | Human Gate |
|---|---|---|---|
| Skill supply-chain risk | Map and audit before install | Unknown repo or unreviewed scripts | Install approval |
| Prompt/document injection | Treat external docs as data, not instructions | External doc asks for secrets/actions | Security review |
| Secret leak | `.env` ignored, never print keys | Key appears in output/diff/report | Stop and rotate key if leaked |
| Content compliance | No profit guarantees, educational framing only | Script implies guaranteed income/trading result | Human review |
| Sheet drift | Read metadata/range before write; read-back after write | Tab/range mismatch or duplicate IDs | Manual repair |
| Strategy drift | Founder Ops weekly decision log | Daily tasks no longer support Shorts->Live->Telegram->Offer | Founder review |

## Reusable Assets To Create

| Asset | Path | Purpose |
|---|---|---|
| Tutor concept vault | `outputs/learning/study_vault/` | Track concepts Azzam audience is learning and struggling with. |
| Transcript topic extractor spec | `docs/youtube-transcript-topic-workflow.md` | Define how transcript/search skills feed Content Bridge. |
| Platform UX rules | `docs/platform-ux-rules.md` | Rules for Sheet, Markdown report, Telegram, and dashboard surfaces. |
| Aegis guardrail checklist | `docs/aegis-guardrail-checklist.md` | Baseline/evidence/drift checklist before external actions. |
| Founder weekly brief template | `outputs/founder/weekly_founder_brief.md` | Weekly decision artifact for offer/channel growth. |

## Sheet Task Allocation

| Task | Agent | Sheet Tab | Status |
|---|---|---|---|
| T-010 | Learning Tutor Agent | Agent Tasks / Pain Points / Offer Funnel | Backlog |
| T-011 | YouTube Workflow Agent | Remake Candidates / Shorts Pipeline | Backlog |
| T-012 | Platform UX Agent | Dashboard / Daily Report | Backlog |
| T-013 | Aegis Guardrail Auditor | Agent Tasks | Backlog |
| T-014 | Founder Ops Agent | Dashboard / Offer Funnel / Lead Log | Backlog |

## Next Implementation Order

1. Aegis Guardrail Auditor first, because every other imported skill increases surface area.
2. YouTube Workflow Agent second, because transcripts/topics improve Shorts quality immediately.
3. Learning Tutor Agent third, because it turns content into Telegram nurture and mini-course assets.
4. Founder Ops Agent fourth, because weekly strategy needs a few days of reports/history.
5. Platform UX Agent runs as review pass after each dashboard/sheet/Telegram change.

## Acceptance Criteria

- No third-party skill is installed before a source audit and human approval.
- Every new agent has a clear input, output, and non-responsibility boundary.
- `daily_status.md` still remains the one-page operating output.
- Google Sheet has task rows for the new agents.
- Guardrails preserve: no auto-publish, no live trade, no leaked secrets, no unreviewed sales claims.

## Implementation Status - 2026-09-30

Internal adapters have been added and the upstream skills have now been installed into Codex:

| Source | Local Adapter | Config | Seed Output |
|---|---|---|---|
| tutor-skills | `agents/learning_tutor/` | `tutor-setup`, `tutor` | `outputs/learning/study_vault/` |
| youtube-skills | `agents/youtube_workflow/` | `youtube-full` | `outputs/youtube_workflow/` |
| platform-design-skills | `agents/platform_ux/` | `web`, `ios`, `android`, `macos`, `ipados`, `watchos`, `tvos`, `visionos` | `docs/platform-ux-rules.md`, `outputs/audit/platform_ux_review.md` |
| Aegis | `auditors/aegis_guardrail/` | `using-aegis`, `establishing-project-context`, `anti-entropy-governance`, `recording-architecture-decisions`, `long-task-continuation`, `first-principles-review` | `docs/aegis-guardrail-checklist.md`, `outputs/audit/aegis_guardrail_report.md` |
| founder-skills | `agents/founder_ops/` | `sop-creator`, `cro-optimization`, `viral-hook-creator`, `lead-magnet-generator`, `strategic-planning`, `go-to-market-plan`, `x-writer`, `linkedin-writer`, `outreach-specialist`, `competitor-intel`, `brand-copywriter`, `pricing-strategist`, `prd-generator`, `product-hunt-launch-plan`, `marketing-ideas` | `outputs/founder/weekly_founder_brief.md`, `knowledge/distilled/founder-context.md` |

The active order is:

```text
aegis_guardrail
-> youtube_data
-> youtube_workflow
-> content_bridge
-> learning_tutor
-> platform_ux
-> hermes_dashboard
-> google_sheet_operator
-> aegis_guardrail read-back
-> founder_ops weekly review
```
