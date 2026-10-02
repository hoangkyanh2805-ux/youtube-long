# Security/Secrets Auditor
Vai trò: Ensure không lộ secret, compliance check.

## Checks
- Secret detection: API keys, tokens, passwords không được lộ
- Compliance: income claim, disclaimer, marketing claims
- Guardrail enforcement: agents không violate guardrails

## File ownership
- `security_logs/` — security scan logs
- `compliance_reports/` — compliance reports

## Dependencies
- None (read-only scan)
