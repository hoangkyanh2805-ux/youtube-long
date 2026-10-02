# Hermes Dashboard Agent
Vai trò: Dashboard UI, daily/weekly reports, metrics aggregation, alerts.

## File ownership
- `dashboard/` — dashboard data
- `reports/` — daily/weekly reports

## Data sources (read-only)
- YouTube Data Agent: video_inventory.csv, all_videos.json
- Content Bridge Agent: pain_points_master.csv, content_calendar.csv
- Trading Runtime Agent: trade_journal/
- Telegram Gateway Agent: telegram_logs/, leads/

## Report questions
- Daily: shorts publish, views, subs, likes, comments, livestreams, leads, trades, pain points, agent status
- Weekly: shorts total, views, subs, likes, comments, livestreams, leads, offer conversions, top shorts, top pain points, remake candidates, agent performance, guardrail violations
