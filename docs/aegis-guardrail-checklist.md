# Aegis Guardrail Checklist

Purpose: adapt `GanyuanRan/Aegis` to the Azzam YouTube Channel Doctor workflow.

## Preflight

- Read baseline docs: `README.md`, `docs/operating-model.md`, `docs/ai-workflow-blueprint.md`, `knowledge/prompt-registry.md`, `multi_agent_architecture.md`, `PROJECT_STATUS_REPORT.md`, `docs/github-skill-pack-agent-map.md`.
- Require a Run Record under `outputs/runs/` before execution.
- Enforce **No Five, No Run**: Workflow ID, automation level, owner, approval gate and output path must be present.
- Validate the Run Record with `python scripts/validate_run_record.py <record>`.
- Confirm file ownership before writing.
- Confirm generated output path is inside the project workspace.
- Scan for secrets before writing reports or messages.
- Check compliance claims: no guaranteed profit, no certain income, no personal financial advice.
- Check whether the next action is external: Sheet sync, Telegram send, YouTube publish, paid API run.

## Human Approval Gates

Human approval is required before:

- Installing third-party skills globally.
- Running paid/bulk TranscriptAPI or Apify jobs.
- Publishing YouTube videos or Shorts.
- Sending Telegram broadcasts or offer messages.
- Changing pricing, offer terms, or funnel promises.
- Destructive Google Sheet rewrites.

## External and paid data gate

- Apify and similar paid/bulk collection requires a Run Record that names exact platforms, public source URLs/accounts, item limits, estimated cost and retention period.
- Require Alan's explicit approval before starting a paid/bulk Actor run.
- Store API tokens only in the active YouTube profile/project `.env`; never in source, MCP config, logs or Run Records.
- Minimize personal data and preserve source/run evidence for every normalized comment.

## Post-Action Evidence

- For Sheet sync: record target tab/range and read-back result.
- For file generation: record output paths.
- For content generation: record review status.
- For any stopped action: record stop reason and safe next options.

## Stop Conditions

- Baseline cannot be read.
- Real secrets appear in output.
- A claim implies guaranteed profit.
- The workflow drifts from `Shorts -> Live -> Telegram -> Offer`.
- An external action has no approval or read-back path.
- A tool/API fails 3 times.

