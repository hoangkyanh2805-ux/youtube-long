# Run Records

Mỗi task vận hành phải có một Run Record trước khi Agent bắt đầu.

## Naming

```text
RUN-YYYYMMDD-WFNN-short-slug.md
```

## Required core

- Workflow ID.
- Automation level.
- Primary owner.
- Human approval requirement/status.
- Output path.

Template: `templates/run-record.md`  
Operating model: `docs/operating-model.md`

## Validation

```bash
python scripts/validate_run_record.py outputs/runs
```

Run Record là task state và audit trail. Không đặt secret trong file này.
