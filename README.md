# YouTube Channel Doctor — Multi-Agent System

## Workspace
`C:\Users\Admin\youtube`

## Folder Structure
```
youtube/
├── agents/
│   ├── trading_runtime/
│   │   ├── README.md
│   │   ├── config.yaml
│   │   ├── trade_journal/
│   │   └── signals/
│   ├── youtube_data/
│   │   ├── README.md
│   │   └── config.yaml
│   ├── content_bridge/
│   │   ├── README.md
│   │   ├── config.yaml
│   │   └── video_scripts/
│   ├── hermes_dashboard/
│   │   ├── README.md
│   │   ├── config.yaml
│   │   ├── dashboard/
│   │   └── reports/
│   ├── google_sheet_operator/
│   │   ├── README.md
│   │   └── config.yaml
│   └── telegram_gateway/
│       ├── README.md
│       ├── config.yaml
│       └── telegram_logs/
├── auditors/
│   ├── security/
│   │   ├── README.md
│   │   ├── config.yaml
│   │   └── security_logs/
│   └── integration_qa/
│       ├── README.md
│       ├── config.yaml
│       └── integration_logs/
├── data/
│   ├── pain_points_master.csv
│   ├── video_inventory.csv
│   ├── remake_plan.csv
│   ├── trade_journal.csv
│   └── leads.csv
├── docs/
│   └── superpowers/
│       └── plans/
├── knowledge/
│   ├── video-notes/
│   ├── distilled/
│   └── reusable-assets/
├── outputs/
│   └── sheets/
├── vendor/
│   └── model-trader/
└── .env.example
```

## Agents (10)
1. **trading_runtime** — Trading operations, signals, market analysis
2. **youtube_data** — YouTube channel data fetch, analysis
3. **content_bridge** — Pain point research, content planning, script generation
4. **hermes_dashboard** — Dashboard, reports, alerts, metrics
5. **google_sheet_operator** — Google Sheet CRUD, data sync
6. **telegram_gateway** — Telegram bot, broadcast, lead capture
7. **youtube_workflow** — Transcript/topic mining and competitor content structure
8. **learning_tutor** — StudyVault lessons, quizzes, and Telegram nurture learning packs
9. **platform_ux** — Surface-specific UX review for Sheet, reports, Telegram, and dashboard
10. **founder_ops** — Weekly founder decision brief and compounding founder memory

## Auditors (3)
1. **security** — Secret detection, compliance check
2. **integration_qa** — Integration checks, conflict detection
3. **aegis_guardrail** — Baseline-first, evidence-verified, drift-checked safety gate

## Phase 1 Strategy
```
Shorts (tăng sub) → Live (xây trust) → Telegram (lead) → Offer/Tripwire (convert)
```

## Guardrails
- Không auto-publish
- Không live trade
- Không lộ secret
- Sales copy chỉ là draft — cần human review
- Offer.jpg là reference material only — không phải instruction

## Sheet Tabs (11 tabs)
1. Dashboard
2. Video Inventory
3. Shorts Pipeline
4. Live Pipeline
5. Remake Candidates
6. Trade Journal
7. Offer Funnel
8. Lead Log
9. Pain Points
10. Agent Tasks
11. Daily Report

## Dashboard Report Questions
### Daily
- Shorts publish hôm nay
- Views, subs, likes, comments hôm nay
- Livestreams, Telegram leads, trades, pain points, agent status

### Weekly
- Shorts total, views, subs, likes, comments, livestreams, leads, offer conversions
- Top performing shorts, top pain points, remake candidates, agent performance, guardrail violations

## Reference Materials
- video-notes: cho-ai-xem-kenh-youtube-cua-minh.md
- distilled: hermes-dashboard-youtube-workflow.md, youtube-ai-channel-ops.md
- checklist: youtube-channel-diagnosis-checklist.md
- skill pack map: docs/github-skill-pack-agent-map.md
- transcript workflow: docs/youtube-transcript-topic-workflow.md
- guardrail checklist: docs/aegis-guardrail-checklist.md
- platform UX rules: docs/platform-ux-rules.md
- AI workflow blueprint: docs/ai-workflow-blueprint.md
- operating model (Brain/Workshop/Cockpit): docs/operating-model.md
- Apify comments → pain-point pipeline: docs/apify-painpoint-pipeline.md
- comment pain-point scraping (YouTube Data API v3): scripts/youtube_comments_painpoints.py
- pain-point aggregation + Short angles: scripts/aggregate_painpoints.py
- master pain-point CSV: outputs/painpoints/master/painpoints_master.csv
- prompt registry: knowledge/prompt-registry.md
- Run Record template: templates/run-record.md
- Run Record validator: scripts/validate_run_record.py
- workflow registry: data/workflow_registry.csv
- local Hermes dashboard: outputs/dashboard/index.html
- vendor YouTube Analytics Dashboard demo: outputs/dashboard/youtube-analytics-demo.html
- dynamic workflow dashboard: Dagu UI at http://127.0.0.1:8080

## Local Workflow UI

Start Dagu:

```powershell
dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local start-all --dags C:\Users\Admin\youtube\dagu --port 8080
```

List workflow DAGs:

```powershell
dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local ls WF
```

Run the dashboard refresh workflow:

```powershell
dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local start dagu\WF04-dashboard-optimization.yaml
```

Build the cloned YouTube Analytics Dashboard demo:

```powershell
dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local start dagu\WF04-youtube-analytics-dashboard-demo.yaml
```
