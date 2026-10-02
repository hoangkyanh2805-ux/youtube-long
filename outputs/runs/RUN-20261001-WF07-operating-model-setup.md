# RUN-20261001-WF07-operating-model-setup

- Goal: Thiết lập mô hình 1 Brain, 1 Workshop, 1 Cockpit và bắt buộc Run Record cho project YouTube.
- Workflow: WF07
- Automation level: L2
- Owner: Hermes Orchestrator
- Supporting agents: founder_ops, hermes_dashboard, integration_qa, aegis_guardrail
- Status: COMPLETE
- Inputs: Đề xuất vận hành của Alan; ai-workflow-blueprint.md; prompt-registry.md; multi_agent_architecture.md; aegis-guardrail-checklist.md
- Missing inputs: NONE
- Tools allowed: Local file read/write, validator, unit tests
- Tools prohibited: Sheet write, Telegram send, YouTube publish, paid or bulk external API
- Guardrail result: PASS - local repository changes only; no external side effect
- Human approval required: NO - Alan requested setup and scope is L2 local files only
- Human approval status: NOT_REQUIRED
- Output paths: docs/operating-model.md; templates/run-record.md; scripts/validate_run_record.py; tests/test_validate_run_record.py; outputs/runs/README.md
- External action: NONE
- External action read-back: NOT_REQUIRED
- Feedback destination: Prompt Registry and Founder Memory after Alan review
- Next owner/action: Alan reviews operating model in VS Code; future tasks must create a validated Run Record

## Plan

1. Document Brain/Workshop/Cockpit ownership and Source-of-Truth.
2. Add reusable Run Record template and validator.
3. Add validator tests and run repository checks.
4. Register files in README and strengthen Aegis preflight.

## Evidence and Sources

- `docs/ai-workflow-blueprint.md`
- `knowledge/prompt-registry.md`
- `multi_agent_architecture.md`
- `docs/aegis-guardrail-checklist.md`

## Results

- Operating model and Run Record controls created locally.
- External systems were not modified.

## Validation

- Command/check: `python -m unittest tests.test_validate_run_record` and `python scripts/validate_run_record.py outputs/runs/RUN-20261001-WF07-operating-model-setup.md`.
- Result: 6 tests passed; Run Record returned `VALID`.

## Approval Log

- 2026-10-01 15:52 +0700 — Alan requested local operating-model setup in the Telegram project thread.

## Feedback

- Pending Alan review in VS Code.
