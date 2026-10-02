# Next Implementation Readiness Review

Date: 2026-09-30

Purpose: summon the installed agent/skill layer, check what is ready, and identify the missing pieces before continuing the YouTube Channel Doctor rollout.

## Skills Now Available

| Area | Installed Skills | Use In This Project |
|---|---|---|
| YouTube research | `youtube-full` | Fetch transcripts, channel latest videos, channel popular videos, and competitor topic signals through TranscriptAPI. |
| Tutor / nurture | `tutor-setup`, `tutor` | Turn approved Shorts/live notes into StudyVault lessons and quizzes for Telegram nurture. |
| Founder growth | `viral-hook-creator`, `lead-magnet-generator`, `strategic-planning`, `go-to-market-plan`, `brand-copywriter`, `cro-optimization`, `competitor-intel`, `marketing-ideas` | Improve hooks, lead magnets, offer copy, weekly growth decisions, and competitor strategy. |
| Platform design | `web`, `ios`, `android`, `macos`, `ipados`, `watchos`, `tvos`, `visionos` | Review dashboard, Sheet, Telegram, and any future mobile/web interfaces for platform fit. |
| Aegis governance | `using-aegis`, `establishing-project-context`, `anti-entropy-governance`, `recording-architecture-decisions`, `long-task-continuation`, `first-principles-review` | Keep owner boundaries, evidence checks, baseline discipline, and long-task continuity. |

## Current State

- Public YouTube data scripts exist and have processed inventory/remake candidates.
- Content Bridge has generated 10 draft Shorts, but all are still `Backlog` and `Needs human review`.
- The learning tutor, YouTube workflow, platform UX, Aegis guardrail, and founder ops agents now have configs and seed outputs.
- `.env` exists, and local checks show `YT_API_KEY`, `TELEGRAM_BOT_TOKEN`, and `APIFY_TOKEN` are configured.
- `TRANSCRIPT_API_KEY` has been configured after the review.
- Telegram bot runtime is verified. Sends have been tested against the configured group topic.
- `TELEGRAM_CHAT_ID=-1004458375752` and `TELEGRAM_THREAD_ID=2` are configured locally in `.env`.
- Google Sheets credential env mismatch has been fixed in config by supporting both `GOOGLE_SHEETS_CREDENTIALS_PATH` and `GOOGLE_APPLICATION_CREDENTIALS`.
- Google Sheets service account JSON is configured locally and live Sheet apply/read-back is verified.
- `pytest` and `google-auth` have been installed after the review.

## Blockers Before Real Execution

| Gap | Impact | Owner | Fix |
|---|---|---|---|
| Live YouTube approval decision | `S-RC-API-001` is still a draft review packet until human approval. | Content Operator | Approve or request remake before recording/publishing. |
| Production scheduling | Telegram and Sheets are verified manually, but no daemon/cron is installed yet. | Ops Agent | Add scheduled runtime only after first approved manual loop. |
| YouTube private analytics | Public data and TranscriptAPI work, but private retention/CTR metrics are not connected. | YouTube Analytics Agent | Defer until the first Telegram/checklist experiment proves demand. |

## Build Next

1. **Transcript enrichment, local only**
   - Use `youtube-full` after `TRANSCRIPT_API_KEY` is configured.
   - Enrich the top 5 remake candidates into `data/processed/transcript_topics.csv`.
   - Update `outputs/youtube_workflow/topic_briefs.md` and `hook_library.md`.

2. **Approve one Short and build its nurture path**
   - Move `S-RC-API-001` from `Backlog` to `Ready` only after human review.
   - Use `viral-hook-creator` and `lead-magnet-generator` to sharpen the hook and `CHECKLIST` CTA.
   - Use `tutor-setup` / `tutor` pattern to turn it into one lesson and quiz.

3. **Telegram dry-run**
   - Implement a command preview for `/report`, `/next`, and `CHECKLIST`.
   - No broadcast until Aegis approves preview and target chat.
   - For a group or forum thread: create/add the bot, send any message in the target chat/thread, run `python scripts/telegram_gateway.py --discover-chat-id`, then copy `chat_id` and optional `thread_id` to `.env` or the send command.

4. **Sheet sync read-back**
   - Done: credential env var mismatch is fixed.
   - Done: apply/read-back workflow writes `video_inventory`, `remake_plan`, and `shorts_pipeline`.
   - Done: live apply created `shorts_pipeline` and verified read-back in `outputs/sheets/sheet_apply_report.json`.
   - Keep future destructive sheet rewrites behind explicit approval.

5. **Founder weekly loop**
   - Use `strategic-planning` and `marketing-ideas` after the first real Short/Telegram experiment.
   - Output one weekly decision only: next move, proof metric, stop/defer item.

## Defer

- YouTube Analytics API retention and private metrics: useful later, but not required before the first `CHECKLIST` experiment.
- Full production Telegram bot deployment: start with dry-run + approved-send.
- Mobile/platform-specific app work: use `web` first unless a real app surface appears.
- Pricing strategy: defer until Telegram lead data exists.

## Acceptance Criteria For The Next Sprint

- Top 5 remake candidates have transcript/topic enrichment or explicit `missing_key` status.
- One Short is human-reviewed and marked `Ready`.
- One `CHECKLIST` learning pack exists with lesson, quiz, and Telegram preview.
- Google Sheet sync has a verified live read-back path.
- Telegram sends nothing externally without an approved preview.
- Aegis report records pass/fail before any external write/send/publish.

## Commands Added

```powershell
python scripts\telegram_gateway.py --dry-run --command /report
python scripts\telegram_gateway.py --discover-chat-id
python scripts\telegram_gateway.py --send --command /report --approve APPROVE

python scripts\sheet_sync_payload.py
python scripts\google_sheet_apply.py --payload outputs\sheets\sheet_sync_payload.json --approve APPLY
```
