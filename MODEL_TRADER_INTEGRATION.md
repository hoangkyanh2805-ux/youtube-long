# Model Trader Integration - YouTube Channel Doctor

**Project root:** `C:\Users\Admin\youtube`  
**Vendored repo:** `C:\Users\Admin\youtube\vendor\model-trader`  
**Source repo:** `https://github.com/tonbistudio/model-trader.git`  
**Requested `model-trade` repo:** checked, but GitHub returned `Repository not found`.

## 1. Why this repo is used

`model-trader` is a framework for turning trader content into a structured trading workflow:

```text
trader content -> transcripts -> strategy.md -> scanner gates -> paper trader -> trade journal -> YouTube content
```

For this YouTube project, the useful parts are:

- `pipeline/fetch_youtube_transcripts.py`: pull captions from trading videos.
- `pipeline/extract_strategy.py`: distill transcripts into `strategy.md` and `philosophy_draft.md`.
- `pipeline/scaffold_trader.py`: create a trader workspace under `traders/<name>/`.
- `model_trader/`: reusable scanner, detectors, backtest, paper trader, monitor.
- `pipeline/youtube_content_generator.py`: local custom bridge that turns paper-trader journals into Shorts ideas, long-form outlines, hooks, lessons and CTAs.

## 2. How it fits this project

This project has two jobs:

1. **Channel doctor / growth layer**
   - Read YouTube channel data.
   - Compare competitor data.
   - Choose remake opportunities.
   - Generate scripts, hooks and CTAs.

2. **Trading-model content layer**
   - Use trader logic from `model-trader`.
   - Run or simulate paper trades.
   - Turn trade outcomes into content.
   - Feed content ideas back into the YouTube plan.

The connection point is the trader journal:

```text
vendor/model-trader/traders/<trader_name>/trades.json
        -> pipeline/youtube_content_generator.py
        -> Shorts scripts / weekly recaps / setup breakdowns
        -> YouTube remake plan and content calendar
```

## 3. Recommended folder layout

```text
C:\Users\Admin\youtube\
├── README.md
├── PROJECT_STATUS_REPORT.md
├── MODEL_TRADER_INTEGRATION.md
├── .env.example
├── knowledge\
├── azzam_search.json
├── gta_search.json
└── vendor\
    └── model-trader\
        ├── model_trader\
        ├── pipeline\
        ├── docs\
        └── traders\
```

Use `C:\Users\Admin\youtube` as the one project root for VSCode, Codex and Hermes/tele gateway.

## 4. Setup commands

Run these from `C:\Users\Admin\youtube\vendor\model-trader`:

```powershell
python -m pip install -e ".[pipeline]"
```

Optional later, only if needed:

```powershell
python -m pip install -e ".[agent]"
python -m pip install -e ".[live]"
```

Do not put real API keys into Markdown. Use `.env` or your secret manager.

## 5. First practical workflow

### Step 1 - Pick or create trader workspace

Existing local trader folders currently include:

- `traders/azzam_master`
- `traders/azammaster_master`

If making a clean new one:

```powershell
python -m pipeline.scaffold_trader azzam_master_v2
```

### Step 2 - Add trader transcripts

Use YouTube video IDs from relevant Azzam/trading videos:

```powershell
python -m pipeline.fetch_youtube_transcripts traders/azzam_master_v2/transcripts VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3
```

You can also manually place `.txt` transcripts into:

```text
vendor/model-trader/traders/azzam_master_v2/transcripts/
```

### Step 3 - Extract strategy

Requires `ANTHROPIC_API_KEY` if using the extraction script.

```powershell
python -m pipeline.extract_strategy traders/azzam_master_v2/transcripts traders/azzam_master_v2
```

Expected outputs:

- `strategy.md`
- `philosophy_draft.md`

### Step 4 - Implement scanner gates

Edit:

```text
vendor/model-trader/traders/<trader_name>/scanner.py
```

The gates should represent trading logic as pass/fail checks, for example:

- market bias gate
- liquidity sweep gate
- FVG / imbalance gate
- confirmation gate
- risk/reward gate
- final entry/stop/target gate

### Step 5 - Backtest and run paper trader

From the trader folder:

```powershell
python backtest.py
python main.py
```

Paper trades should land in:

```text
vendor/model-trader/traders/<trader_name>/trades.json
```

### Step 6 - Generate YouTube content from journal

From `vendor/model-trader`:

```powershell
python pipeline/youtube_content_generator.py traders/<trader_name>/trades.json
```

Use the output to create:

- Shorts script ideas.
- Loss lesson clips.
- Win highlight clips.
- Weekly recap long videos.
- Setup breakdown long videos.
- CTA/comment prompts.

## 6. How Tele Gateway should use it

Tele gateway should not directly publish or trade. It should trigger safe commands and return summaries.

Suggested Telegram commands:

| Command | Action |
|---------|--------|
| `/status` | Show project status and latest report summary. |
| `/diagnose` | Run YouTube channel doctor summary from existing JSON/report data. |
| `/content` | Generate content ideas from latest `trades.json`. |
| `/remake` | Suggest remake candidates from channel/video inventory. |
| `/next` | Show next recommended action. |

Guardrails:

- No secret values in Telegram messages.
- No automatic publish without approval.
- No live trading command through Telegram.
- Log every command input/output to a local log file when gateway code is added.

## 7. Immediate next build steps

1. Open VSCode at `C:\Users\Admin\youtube`.
2. Install `model-trader` editable dependencies from `vendor/model-trader`.
3. Decide whether to keep `azzam_master`, `azammaster_master`, or create `azzam_master_v2`.
4. Run transcript/strategy pipeline for selected trading videos.
5. Generate first content calendar from either `trades.json` or a mock journal.
6. Add a small `gateway/` service later for Telegram commands.

## 8. Current caveats

- `https://github.com/tonbistudio/model-trade.git` does not exist at the time checked.
- `vendor/model-trader` came from the existing local clone at `C:\Users\Admin\model-trader`.
- The vendored repo includes local untracked work from the original clone, especially `pipeline/youtube_content_generator.py` and `traders/`.
- This is currently a local integration, not a polished packaged app yet.
