"""Render a one-page Hermes daily status report for Azzam Phase 1."""

from __future__ import annotations

import argparse
import csv
import html
from datetime import date
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def collect_daily_metrics(root: Path, report_date: str) -> dict[str, Any]:
    processed_dir = root / "data" / "processed"
    api_inventory_path = processed_dir / "video_inventory_api.csv"
    inventory_path = api_inventory_path if api_inventory_path.exists() else processed_dir / "video_inventory.csv"
    api_candidates_path = processed_dir / "remake_candidates_api.csv"
    candidates_path = api_candidates_path if api_candidates_path.exists() else processed_dir / "remake_candidates.csv"
    inventory = read_csv(inventory_path)
    candidates = read_csv(candidates_path)
    content = read_csv(root / "outputs" / "content" / "content_calendar.csv")
    channel_snapshots = read_csv(processed_dir / "channel_snapshots.csv")
    live_agenda = root / "outputs" / "content" / "live_agenda.md"

    draft_shorts = [row for row in content if row.get("status") in {"Backlog", "Scripted"}]
    ready_shorts = [row for row in content if row.get("status") in {"Ready", "Scheduled"}]
    top_candidate = top_by_int(candidates, "priority_score")
    top_short = draft_shorts[0] if draft_shorts else {}
    channel_delta = latest_channel_delta(channel_snapshots, "self")

    metrics = {
        "report_date": report_date,
        "api_inventory_available": api_inventory_path.exists(),
        "video_count": len(inventory),
        "short_video_count": count_where(inventory, "format", "short"),
        "live_video_count": count_where(inventory, "format", "live"),
        "remake_candidate_count": len(candidates),
        "views_total": sum_int(inventory, "views"),
        "likes_total": sum_int(inventory, "likes"),
        "comments_total": sum_int(inventory, "comments"),
        "subscriber_delta": channel_delta.get("subscriber_delta"),
        "channel_view_delta": channel_delta.get("channel_view_delta"),
        "channel_delta_from": channel_delta.get("from_date", ""),
        "channel_delta_to": channel_delta.get("to_date", ""),
        "draft_short_count": len(draft_shorts),
        "ready_short_count": len(ready_shorts),
        "top_remake_candidate": top_candidate,
        "top_short": top_short,
        "live_agenda_exists": live_agenda.exists(),
    }
    metrics["next_actions"] = build_next_actions(metrics)
    metrics["risks"] = build_risks(metrics)
    return metrics


def count_where(rows: list[dict], field: str, value: str) -> int:
    return sum(1 for row in rows if row.get(field) == value)


def sum_int(rows: list[dict], field: str) -> int:
    total = 0
    for row in rows:
        try:
            total += int(row.get(field) or 0)
        except ValueError:
            continue
    return total


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def latest_channel_delta(rows: list[dict], role: str) -> dict[str, Any]:
    role_rows = [row for row in rows if row.get("role") == role and row.get("snapshot_at")]
    role_rows.sort(key=lambda row: row.get("snapshot_at", ""))
    if len(role_rows) < 2:
        return {}

    previous = role_rows[-2]
    latest = role_rows[-1]
    previous_subs = int_or_none(previous.get("subscriber_count"))
    latest_subs = int_or_none(latest.get("subscriber_count"))
    previous_views = int_or_none(previous.get("view_count"))
    latest_views = int_or_none(latest.get("view_count"))

    delta: dict[str, Any] = {
        "from_date": previous.get("snapshot_at", ""),
        "to_date": latest.get("snapshot_at", ""),
    }
    if previous_subs is not None and latest_subs is not None:
        delta["subscriber_delta"] = latest_subs - previous_subs
    if previous_views is not None and latest_views is not None:
        delta["channel_view_delta"] = latest_views - previous_views
    return delta


def top_by_int(rows: list[dict], field: str) -> dict:
    if not rows:
        return {}
    return max(rows, key=lambda row: int(row.get(field) or 0))


def build_next_actions(metrics: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    draft_count = metrics.get("draft_short_count", 0)
    ready_count = metrics.get("ready_short_count", 0)
    top_short = metrics.get("top_short") or {}
    top_candidate = metrics.get("top_remake_candidate") or {}

    if draft_count:
        actions.append(f"Review {draft_count} draft Shorts and approve the first one for recording.")
    if top_short:
        actions.append(
            f"Record `{top_short.get('short_id')}` with keyword `{top_short.get('telegram_keyword', 'CHECKLIST')}`."
        )
    if top_candidate:
        actions.append(
            f"Use `{top_candidate.get('candidate_id')}` as the next remake reference: {top_candidate.get('original_title')}."
        )
    if metrics.get("subscriber_delta") is not None:
        actions.append(f"Subscriber delta from latest snapshots: {format_signed(metrics.get('subscriber_delta'))}.")
    if metrics.get("live_agenda_exists"):
        actions.append("Review `outputs/content/live_agenda.md` and choose a live time.")
    if not ready_count:
        actions.append("Move one reviewed Short from `Backlog` to `Ready` after human approval.")
    return actions


def build_risks(metrics: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    if not metrics.get("video_count"):
        risks.append("No video inventory found; run the YouTube data layer.")
    if not metrics.get("draft_short_count"):
        risks.append("No draft Shorts found; run the Content Bridge.")
    if not metrics.get("ready_short_count"):
        risks.append("No Shorts are marked Ready or Scheduled yet.")
    if not metrics.get("live_agenda_exists"):
        risks.append("No live agenda exists yet.")
    if metrics.get("api_inventory_available"):
        risks.append("YouTube Data API stats are available, but subscriber delta and retention still need private analytics or repeated snapshots.")
    else:
        risks.append("Public search exports do not include real views, comments, or subscriber gain yet.")
    return risks


def format_signed(value: Any) -> str:
    number = int_or_none(value)
    if number is None:
        return "n/a"
    return f"+{number}" if number >= 0 else str(number)


def render_daily_report(metrics: dict[str, Any]) -> str:
    top_candidate = metrics.get("top_remake_candidate") or {}
    top_short = metrics.get("top_short") or {}
    lines = [
        f"# Azzam Daily Status - {metrics.get('report_date', '')}",
        "",
        "## Snapshot",
        "",
        f"- Video inventory rows: {metrics.get('video_count', 0)}",
        f"- Shorts found: {metrics.get('short_video_count', 0)}",
        f"- Live videos found: {metrics.get('live_video_count', 0)}",
        f"- Remake candidates: {metrics.get('remake_candidate_count', 0)}",
        f"- Total views in inventory: {metrics.get('views_total', 0)}",
        f"- Total likes in inventory: {metrics.get('likes_total', 0)}",
        f"- Total comments in inventory: {metrics.get('comments_total', 0)}",
        f"- Subscriber delta: {format_signed(metrics.get('subscriber_delta'))}",
        f"- Channel view delta: {format_signed(metrics.get('channel_view_delta'))}",
        f"- Draft Shorts generated: {metrics.get('draft_short_count', 0)}",
        f"- Ready/Scheduled Shorts: {metrics.get('ready_short_count', 0)}",
        "",
        "## Today Next Actions",
        "",
    ]
    lines.extend(format_bullets(metrics.get("next_actions", [])))
    lines.extend(
        [
            "",
            "## Top Draft Short",
            "",
            f"- ID: {top_short.get('short_id', 'None')}",
            f"- Title: {top_short.get('title', 'None')}",
            f"- Telegram keyword: {top_short.get('telegram_keyword', 'None')}",
            "",
            "## Top Remake Candidate",
            "",
            f"- ID: {top_candidate.get('candidate_id', 'None')}",
            f"- Priority: {top_candidate.get('priority_score', 'None')}",
            f"- Title: {top_candidate.get('original_title', 'None')}",
            "",
            "## Risks / Blockers",
            "",
        ]
    )
    lines.extend(format_bullets(metrics.get("risks", [])))
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Drafts require human review before recording or publishing.",
            "- No auto-publish path is enabled.",
            "- No trading execution path is enabled.",
            "- No guaranteed-profit claims.",
            "",
        ]
    )
    return "\n".join(lines)


def render_dashboard_html(metrics: dict[str, Any]) -> str:
    """Render a static local dashboard for fast cockpit review."""
    report_date = escape(metrics.get("report_date", ""))
    top_candidate = metrics.get("top_remake_candidate") or {}
    top_short = metrics.get("top_short") or {}
    next_actions = metrics.get("next_actions", [])
    risks = metrics.get("risks", [])
    generated_note = "Generated from local CSV/Markdown workspace data."

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Azzam Hermes Dashboard - {report_date}</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --surface: #ffffff;
      --surface-strong: #101828;
      --text: #101828;
      --muted: #5f6b7a;
      --border: #d7dde5;
      --blue: #175cd3;
      --green: #067647;
      --amber: #b54708;
      --red: #b42318;
      --focus: #1d4ed8;
      color-scheme: light dark;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #111418;
        --surface: #191e24;
        --surface-strong: #e6edf5;
        --text: #edf2f7;
        --muted: #a9b4c2;
        --border: #374151;
        --blue: #8ab4ff;
        --green: #62d49f;
        --amber: #f6bd60;
        --red: #ff8a80;
        --focus: #93c5fd;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ font-size: 100%; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, "Segoe UI", Arial, sans-serif;
      line-height: 1.5;
    }}
    a {{ color: var(--blue); }}
    a:focus-visible {{
      outline: 0.1875rem solid var(--focus);
      outline-offset: 0.1875rem;
    }}
    .skip-link {{
      position: absolute;
      inset-block-start: -10rem;
      inset-inline-start: 1rem;
      background: var(--surface-strong);
      color: var(--bg);
      padding: 0.75rem 1rem;
      z-index: 10;
    }}
    .skip-link:focus {{ inset-block-start: 1rem; }}
    header {{
      background: var(--surface);
      border-block-end: 1px solid var(--border);
    }}
    .shell {{
      inline-size: min(100% - 2rem, 76rem);
      margin-inline: auto;
    }}
    .topbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      align-items: end;
      justify-content: space-between;
      padding-block: 1.25rem;
    }}
    h1, h2, h3 {{ line-height: 1.2; margin: 0; }}
    h1 {{ font-size: 2rem; }}
    h2 {{ font-size: 1.1rem; }}
    h3 {{ font-size: 1rem; }}
    main {{ padding-block: 1.25rem 2rem; }}
    .status-line {{
      color: var(--muted);
      margin-block: 0.35rem 0;
      max-inline-size: 72ch;
    }}
    .badge-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-block-start: 0.75rem;
    }}
    .badge {{
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.25rem 0.65rem;
      background: var(--bg);
      font-size: 0.875rem;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 1rem;
    }}
    .kpis {{
      grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
      margin-block-end: 1rem;
    }}
    .panel, .kpi {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 0.5rem;
      padding: 1rem;
    }}
    .kpi strong {{
      display: block;
      margin-block-start: 0.35rem;
      font-size: 1.7rem;
      line-height: 1;
      font-variant-numeric: tabular-nums;
    }}
    .label {{ color: var(--muted); font-size: 0.875rem; }}
    .content-grid {{
      grid-template-columns: 1fr;
    }}
    @media (min-width: 58rem) {{
      .content-grid {{ grid-template-columns: 1.2fr 0.8fr; align-items: start; }}
    }}
    ul {{ padding-inline-start: 1.2rem; margin-block-end: 0; }}
    li + li {{ margin-block-start: 0.45rem; }}
    .metric-row {{
      display: grid;
      grid-template-columns: minmax(8rem, 1fr) auto;
      gap: 0.75rem;
      border-block-start: 1px solid var(--border);
      padding-block: 0.7rem;
    }}
    .metric-row:first-of-type {{ border-block-start: 0; }}
    .value {{ font-variant-numeric: tabular-nums; font-weight: 700; }}
    .ok {{ color: var(--green); }}
    .warn {{ color: var(--amber); }}
    .risk {{ color: var(--red); }}
    footer {{
      border-block-start: 1px solid var(--border);
      color: var(--muted);
      padding-block: 1rem;
      font-size: 0.875rem;
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        scroll-behavior: auto !important;
      }}
    }}
    @media (prefers-contrast: more) {{
      :root {{ --muted: var(--text); --border: var(--text); }}
      .panel, .kpi, .badge {{ border-width: 2px; }}
    }}
  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header>
    <div class="shell topbar">
      <div>
        <h1>Azzam Hermes Dashboard</h1>
        <p class="status-line">Run Mode: Local L2. {escape(generated_note)}</p>
        <div class="badge-row" aria-label="Dashboard status">
          <span class="badge">Report date: {report_date}</span>
          <span class="badge">External action: NONE</span>
          <span class="badge">Approval: local review</span>
        </div>
      </div>
      <p class="status-line"><a href="../reports/daily_status.md">Open daily_status.md</a></p>
    </div>
  </header>
  <main id="main-content" class="shell">
    <section aria-labelledby="snapshot-heading">
      <h2 id="snapshot-heading">Snapshot</h2>
      <div class="grid kpis" role="list">
        {render_kpi("Videos", metrics.get("video_count", 0))}
        {render_kpi("Shorts", metrics.get("short_video_count", 0))}
        {render_kpi("Lives", metrics.get("live_video_count", 0))}
        {render_kpi("Views", metrics.get("views_total", 0))}
        {render_kpi("Likes", metrics.get("likes_total", 0))}
        {render_kpi("Comments", metrics.get("comments_total", 0))}
        {render_kpi("Draft Shorts", metrics.get("draft_short_count", 0))}
        {render_kpi("Ready/Scheduled", metrics.get("ready_short_count", 0))}
      </div>
    </section>
    <div class="grid content-grid">
      <section class="panel" aria-labelledby="actions-heading">
        <h2 id="actions-heading">Today Next Actions</h2>
        {render_list(next_actions, "No local actions queued.")}
      </section>
      <section class="panel" aria-labelledby="guardrails-heading">
        <h2 id="guardrails-heading">Guardrails</h2>
        <ul>
          <li class="ok">Drafts require human review before recording or publishing.</li>
          <li class="ok">No auto-publish path is enabled.</li>
          <li class="ok">No trading execution path is enabled.</li>
          <li class="ok">No guaranteed-profit claims.</li>
        </ul>
      </section>
      <section class="panel" aria-labelledby="pipeline-heading">
        <h2 id="pipeline-heading">Pipeline Highlights</h2>
        {render_metric_row("Top draft Short", top_short.get("short_id", "None"))}
        {render_metric_row("Short title", top_short.get("title", "None"))}
        {render_metric_row("Telegram keyword", top_short.get("telegram_keyword", "None"))}
        {render_metric_row("Top remake candidate", top_candidate.get("candidate_id", "None"))}
        {render_metric_row("Candidate priority", top_candidate.get("priority_score", "None"))}
        {render_metric_row("Candidate title", top_candidate.get("original_title", "None"))}
      </section>
      <section class="panel" aria-labelledby="risks-heading">
        <h2 id="risks-heading">Risks / Blockers</h2>
        {render_list(risks, "No risks reported.", item_class="risk")}
      </section>
    </div>
  </main>
  <footer>
    <div class="shell">Generated by Hermes Dashboard from local workspace files. Review in VS Code before any Sheet, Telegram, or YouTube action.</div>
  </footer>
</body>
</html>
"""


def render_kpi(label: str, value: Any) -> str:
    return (
        '<article class="kpi" role="listitem">'
        f'<span class="label">{escape(label)}</span>'
        f"<strong>{escape(format_number(value))}</strong>"
        "</article>"
    )


def render_metric_row(label: str, value: Any) -> str:
    return (
        '<div class="metric-row">'
        f'<span class="label">{escape(label)}</span>'
        f'<span class="value">{escape(value)}</span>'
        "</div>"
    )


def render_list(items: list[str], empty_text: str, item_class: str = "") -> str:
    if not items:
        items = [empty_text]
    class_attr = f' class="{item_class}"' if item_class else ""
    rendered = "".join(f"<li{class_attr}>{escape(item)}</li>" for item in items)
    return f"<ul>{rendered}</ul>"


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def format_number(value: Any) -> str:
    number = int_or_none(value)
    if number is None:
        return str(value)
    return f"{number:,}"


def format_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- {item}" for item in items]


def write_daily_report(root: Path, metrics: dict[str, Any]) -> Path:
    report_dir = root / "outputs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "daily_status.md"
    report_path.write_text(render_daily_report(metrics), encoding="utf-8")
    return report_path


def write_dashboard_html(root: Path, metrics: dict[str, Any]) -> Path:
    dashboard_dir = root / "outputs" / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    dashboard_path = dashboard_dir / "index.html"
    dashboard_path.write_text(render_dashboard_html(metrics), encoding="utf-8")
    return dashboard_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Azzam Hermes daily status report")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()

    metrics = collect_daily_metrics(args.root, args.date)
    report_path = write_daily_report(args.root, metrics)
    dashboard_path = write_dashboard_html(args.root, metrics)
    print(f"wrote {report_path}")
    print(f"wrote {dashboard_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
