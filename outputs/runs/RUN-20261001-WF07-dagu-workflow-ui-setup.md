# RUN-20261001-WF07-dagu-workflow-ui-setup

- Goal: Install and run Dagu as the dynamic workflow dashboard for WF01-WF07.
- Workflow: WF07
- Automation level: L2
- Owner: Hermes Orchestrator
- Supporting agents: hermes_dashboard, integration_qa, aegis_guardrail
- Status: COMPLETE
- Inputs: docs/operating-model.md; docs/ai-workflow-blueprint.md; dagu official quickstart; user approval to install and run Dagu.
- Missing inputs: NONE
- Tools allowed: npm global install for Dagu CLI; local YAML workflow files; local Dagu Web UI; local validation commands.
- Tools prohibited: Sheet write, Telegram send, YouTube publish, paid or bulk external API, workflow steps that load .env secrets.
- Guardrail result: PASS - Dagu runs local workflows only; .env loading disabled in DAGs and workflow working directory moved away from repo root.
- Human approval required: NO - user explicitly approved installing and running local Dagu; all workflows are L2/local or dry-run only.
- Human approval status: NOT_REQUIRED
- Output paths: dagu/WF01-new-topic-video.yaml; dagu/WF02-competitor-backlog.yaml; dagu/WF03-shorts-remake.yaml; dagu/WF04-dashboard-optimization.yaml; dagu/WF05-comment-insight.yaml; dagu/WF06-lead-offer.yaml; dagu/WF07-weekly-review.yaml; .dagu-local/config.yaml
- External action: NONE
- External action read-back: NOT_REQUIRED
- Feedback destination: Operating Model and Founder Memory after Alan review
- Next owner/action: Alan opens http://127.0.0.1:8080, runs WF04 from Dagu UI, and uses WF01-WF07 as the daily workflow cockpit.

## Plan

1. Install Dagu CLI.
2. Create WF01-WF07 Dagu YAML files.
3. Validate YAML and Run Records.
4. Run WF04 end-to-end through Dagu CLI.
5. Start Dagu Web UI at localhost.

## Evidence and Sources

- Dagu docs quickstart: https://docs.dagu.sh/getting-started/quickstart
- `dagu.cmd version`: 2.18.1
- `dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local ls WF`
- `dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local start dagu\WF04-dashboard-optimization.yaml`

## Results

- Dagu CLI installed globally through npm.
- WF01-WF07 workflow YAML files created.
- Dagu Web UI is running at `http://127.0.0.1:8080`.
- WF04 completed through Dagu and refreshed `outputs/dashboard/index.html`.

## Validation

- Command/check: `dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local ls WF`
- Result: WF01-WF07 listed.
- Command/check: `dagu.cmd --dagu-home C:\Users\Admin\youtube\.dagu-local start dagu\WF04-dashboard-optimization.yaml`
- Result: Succeeded; 58 tests passed; dashboard refreshed.
- Command/check: `python scripts\validate_run_record.py outputs\runs`
- Result: 3 existing Run Records valid before this Run Record was added.

## Approval Log

- 2026-10-01 19:00 +0700 - Alan requested installing and running Dagu in the project thread.

## Feedback

- Dagu is the workflow cockpit. The existing static Hermes dashboard remains the business KPI dashboard.
