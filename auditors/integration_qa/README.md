# Integration QA Auditor
Vai trò: Ensure agents integrate correctly, data flows, no conflicts.

## Checks
- File integrity: agents không đạp nhau — file ownership respected
- Data flow: data từ agent này đúng送到 agent khác
- Task coordination: agents không conflict task, no double work
- Error handling: agents handle errors gracefully, log errors

## File ownership
- `integration_logs/` — integration logs
- `conflict_reports/` — conflict reports

## Dependencies
- None (read-only check)
