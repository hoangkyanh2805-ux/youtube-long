# Trading Runtime Agent
Vai trò: Trading operations, market analysis, signal generation, trade journal.

## File ownership
- `trade_journal/` — trade records
- `signals/` — trading signals

## Guardrails
- Chỉ generate signals, NOT execute trades
- Human decide execute or not

## Dependencies
- Market data API (nếu có)
- YouTube Data API (cho context)
