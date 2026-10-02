"""
Build the operating dashboard — one page that shows the whole pipeline state,
plus the two Telegram topics and what each role does.

Reads real data from the repo, writes a self-contained static HTML.
No server needed: open the file in a browser.

Writes: outputs/dashboard/ops.html
"""
from __future__ import annotations

import csv
import json
import socket
import sys
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

OUT = Path("outputs/dashboard")
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = [
    ("EDIT", "205", "Content đã duyệt → editor lấy làm việc",
     "Báo cáo content brief, hook, CTA, quy trình"),
    ("COMMENT", "206", "Cào comment + pain point → Alan duyệt",
     "Top pain point mới, link nguồn, yêu cầu duyệt"),
    ("GENERAL", "2", "Báo cáo tổng hợp", "Daily status, pipeline health"),
]

PIPELINE = [
    ("1", "Cào comment", "competitor_longform_scrape.py",
     "YouTube API → comment → pain point", "Hàng ngày"),
    ("2", "Phân tích pain", "extract_painpoints.py",
     "Lọc spam + domain + chấm điểm", "Hàng ngày"),
    ("3", "Chốt content", "build_strategy.py",
     "Sales angle + keyword + backlog", "Hàng tuần"),
    ("4", "Alan duyệt", "Telegram topic COMMENT (206)",
     "Duyệt pain point → chốt 3 Short + 1 Long", "Hàng ngày"),
    ("5", "Gửi brief", "telegram_reporter.py --report content_brief",
     "Đẩy brief sang topic EDIT (205)", "Hàng ngày"),
    ("6", "Editor dựng", "CapCut MCP + CapCut Pro",
     "MCP dựng draft → editor polish → export", "Hàng ngày"),
    ("7", "QC + đăng", "Checklist 8 điểm",
     "Guardrail chặn đăng nếu vi phạm", "Hàng ngày"),
    ("8", "Báo cáo", "dagu WF07 + telegram_reporter.py",
     "Weekly review + pipeline health", "Hàng tuần"),
]


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# Kênh mình (Azzam) — Brand Account.
OWNER_ID = "UCBZ7LaffmEPv91sWcfroJdQ"


def to_float(v, d=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def to_int(v, d=0) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return d


def dedupe(rows: list[dict]) -> list[dict]:
    out, seen = [], set()
    for r in rows:
        k = r.get("comment_id") or f"{r.get('content_url','')}|{r.get('comment_text','')[:80]}"
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def mcp_alive() -> bool:
    s = socket.socket()
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", 9001))
        return True
    except Exception:
        return False
    finally:
        s.close()


def main() -> int:
    root = Path(".")

    pain = dedupe(
        load_csv(root / "outputs/competitor_analysis/painpoint_candidates.csv")
        + load_csv(root / "outputs/competitor_longform/painpoint_candidates.csv")
    )
    comments = dedupe(
        load_csv(root / "outputs/competitor_analysis/normalized_comments.csv")
        + load_csv(root / "outputs/competitor_longform/normalized_comments.csv")
    )
    backlog = load_csv(root / "outputs/strategy/content_backlog.csv")
    angles = load_json(root / "outputs/strategy/sales_angles.json") or []
    videos = load_csv(root / "outputs/competitor_longform/longform_inventory.csv")

    # Analytics thật: private metrics (OAuth) + điểm mù đã phân tích.
    analytics = load_json(root / "vendor/youtube-analytics-dashboard/analytics_latest.json")
    blind = load_json(root / "outputs/reports/blindspots.json")

    mcp = mcp_alive()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    top_pain = sorted(pain, key=lambda x: -to_float(x.get("score")))[:8]
    top_backlog = sorted(backlog, key=lambda x: -to_int(x.get("priority")))[:6]

    # checks
    checks = [
        ("CapCut MCP backend (port 9001)", mcp),
        ("Pain point data", len(pain) > 0),
        ("Content backlog", len(backlog) > 0),
        ("Sales angles", len(angles) > 0),
        ("Asset library", (root / "assets/README.md").exists()),
        ("Prompt pack", (root / "prompts/07_CAPCUT_MCP.md").exists()),
        ("SOP final", (root / "outputs/reports/AZZAM_SOP_FINAL.docx").exists()),
    ]

    def stat(label, value, note=""):
        return f"""<div class="stat"><div class="stat-label">{escape(label)}</div>
<div class="stat-value">{escape(str(value))}</div>
<div class="stat-note">{escape(note)}</div></div>"""

    stat_html = "".join([
        stat("Comment unique", f"{len(comments):,}", "đã dedupe 2 run"),
        stat("Pain point", f"{len(pain):,}", "đã lọc spam + domain"),
        stat("Video đã cào", len(videos), "long-form >60s"),
        stat("Content backlog", len(backlog), "sẵn sàng sản xuất"),
        stat("Sales angles", len(angles), "có evidence link"),
        stat("MCP backend", "Chạy" if mcp else "Tắt",
             "port 9001" if mcp else "chạy capcut_server.py"),
    ])

    check_html = "".join(
        f'<li class="{"ok" if ok else "bad"}">'
        f'<span class="dot"></span>{escape(label)}</li>'
        for label, ok in checks
    )

    topic_html = "".join(f"""
<div class="topic">
  <div class="topic-head">
    <span class="topic-name">{escape(name)}</span>
    <span class="topic-id">thread {escape(tid)}</span>
  </div>
  <div class="topic-purpose">{escape(purpose)}</div>
  <div class="topic-content">{escape(content)}</div>
  <code class="cmd">python scripts/telegram_reporter.py --report {report} --send --approve APPROVE</code>
</div>""" for name, tid, purpose, content, report in [
        ("EDIT", "205", "Content đã duyệt → editor lấy làm việc",
         "Báo cáo content brief, hook, CTA, quy trình", "content_brief"),
        ("COMMENT", "206", "Cào comment + pain point → Alan duyệt",
         "Top pain point mới, link nguồn, yêu cầu duyệt", "comment"),
        ("GENERAL", "2", "Báo cáo tổng hợp",
         "Daily status, pipeline health", "pipeline_health"),
    ])

    pipe_html = "".join(f"""
<tr>
  <td class="num">{escape(n)}</td>
  <td><strong>{escape(step)}</strong></td>
  <td><code>{escape(tool)}</code></td>
  <td>{escape(what)}</td>
  <td class="freq">{escape(freq)}</td>
</tr>""" for n, step, tool, what, freq in PIPELINE)

    pain_html = "".join(f"""
<tr>
  <td class="num">{i}</td>
  <td><span class="tag">{escape(p.get('categories',''))}</span></td>
  <td class="score">{p.get('score')}</td>
  <td class="quote">{escape(str(p.get('comment_text',''))[:160])}</td>
  <td><a href="{escape(p.get('content_url',''))}" target="_blank" rel="noopener">nguồn</a></td>
</tr>""" for i, p in enumerate(top_pain, 1))

    backlog_html = "".join(f"""
<tr>
  <td class="num">{i}</td>
  <td><span class="tag fmt-{escape(str(r.get('format','')).lower())}">{escape(r.get('format',''))}</span></td>
  <td>{escape(r.get('title_draft',''))}</td>
  <td class="small">{escape(r.get('pain_cluster',''))}</td>
  <td class="small">{escape(r.get('cta',''))}</td>
  <td class="score">{r.get('evidence_count','')}</td>
</tr>""" for i, r in enumerate(top_backlog, 1))

    # ---- Analytics thật (private metrics) --------------------------------
    an_html, an_meta = "", ""
    if analytics:
        am = analytics.get("metrics", {})
        dv = blind.get("derived", {}) if blind else {}
        views_a = to_int(am.get("views"))
        an_meta = (f"Cửa sổ {analytics.get('start')} → {analytics.get('end')} "
                   f"({analytics.get('days')} ngày) • OAuth YouTube Analytics API")

        bot = (blind or {}).get("bot_traffic", {})
        bot_v = to_int(bot.get("views"))
        bot_pct = bot.get("pct_of_channel", 0)

        an_html = "".join([
            stat("Views (28d)", f"{views_a:,}", "kênh mình"),
            stat("Watch time", f"{dv.get('watch_hours', round(to_int(am.get('estimatedMinutesWatched'))/60,1))}h",
                 f"avg {to_int(am.get('averageViewDuration'))}s/view"),
            stat("Sub ròng", f"{dv.get('sub_net', 0):+d}",
                 f"+{to_int(am.get('subscribersGained'))} / -{to_int(am.get('subscribersLost'))}"),
            stat("Sub conversion", f"{dv.get('sub_conversion_pct', 0)}%", "ngành 0.5–2%"),
            stat("Comment rate", f"{dv.get('comment_rate_pct', 0)}%",
                 f"{to_int(am.get('comments'))} comment"),
            stat("Traffic nghi bot", f"{bot_v:,}",
                 f"{bot_pct}% tổng view" if bot_v else "không phát hiện"),
        ])

    # Bảng nguồn traffic
    traffic_html = ""
    if analytics:
        ts = analytics.get("traffic_sources", [])
        tot_t = sum(to_int(r[1]) for r in ts) or 1
        traffic_html = "".join(
            f'<tr><td><code>{escape(str(r[0]))}</code></td>'
            f'<td class="score">{to_int(r[1]):,}</td>'
            f'<td class="score">{to_int(r[1])/tot_t*100:.1f}%</td>'
            f'<td class="small">{to_float(r[2]):,.0f} min</td></tr>'
            for r in ts[:8])

    # Bảng nguồn ngoài (phát hiện bot)
    ext_html = ""
    if analytics:
        ex = analytics.get("external_urls", [])
        BOT = ("seofast", "playbot", "viewbot", "like4like", "sub4sub")
        rows_ext = "".join(
            f'<tr><td><code>{escape(str(r[0]))}</code></td>'
            f'<td class="score">{to_int(r[1]):,}</td>'
            f'<td>{"<span class=tag-bot>NGHI BOT</span>" if any(b in str(r[0]).lower() for b in BOT) else ""}</td></tr>'
            for r in ex[:8])
        ext_html = rows_ext

    # Điểm mù
    blind_html = ""
    blind_meta = ""
    if blind:
        fs = blind.get("findings", [])
        blind_meta = (f"{len(fs)} phát hiện • "
                      f"{sum(1 for f in fs if f['severity']=='CRITICAL')} critical • "
                      f"{blind.get('generated_at','')}")
        sev_cls = {"CRITICAL": "sev-critical", "HIGH": "sev-high",
                   "MEDIUM": "sev-medium", "INFO": "sev-info"}
        blind_html = "".join(f"""
<div class="finding {sev_cls.get(f['severity'],'')}">
  <div class="finding-head">
    <span class="sev {sev_cls.get(f['severity'],'')}">{escape(f['severity'])}</span>
    <strong>{escape(f['title'])}</strong>
  </div>
  <div class="finding-body">{escape(f['detail'])}</div>
</div>""" for f in fs)

    html = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Azzam Ops Dashboard — {date.today().isoformat()}</title>
<style>
:root {{
  --bg:#0f1216; --surface:#171c22; --surface2:#1e242c; --border:#2c343d;
  --text:#e6edf5; --muted:#94a3b8; --blue:#60a5fa; --green:#4ade80;
  --amber:#fbbf24; --red:#f87171; --accent:#38bdf8;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  line-height:1.5; padding:24px; }}
.wrap {{ max-width:1280px; margin:0 auto; }}
header {{ border-bottom:1px solid var(--border); padding-bottom:16px; margin-bottom:24px; }}
h1 {{ margin:0 0 4px; font-size:24px; letter-spacing:-0.02em; }}
h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:0.08em;
  color:var(--muted); margin:32px 0 12px; font-weight:600; }}
.sub {{ color:var(--muted); font-size:13px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; }}
.stat {{ background:var(--surface); border:1px solid var(--border);
  border-radius:10px; padding:14px 16px; }}
.stat-label {{ font-size:11px; text-transform:uppercase; letter-spacing:0.06em;
  color:var(--muted); }}
.stat-value {{ font-size:26px; font-weight:700; margin:4px 0 2px;
  font-variant-numeric:tabular-nums; }}
.stat-note {{ font-size:11px; color:var(--muted); }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
@media (max-width:860px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
.card {{ background:var(--surface); border:1px solid var(--border);
  border-radius:10px; padding:16px 18px; }}
ul.checks {{ list-style:none; margin:0; padding:0; }}
ul.checks li {{ display:flex; align-items:center; gap:8px; padding:5px 0;
  font-size:13px; }}
.dot {{ width:8px; height:8px; border-radius:50%; flex:0 0 8px; }}
li.ok .dot {{ background:var(--green); }}
li.bad .dot {{ background:var(--red); }}
li.bad {{ color:var(--red); }}
.topic {{ background:var(--surface); border:1px solid var(--border);
  border-left:3px solid var(--accent); border-radius:8px;
  padding:14px 16px; margin-bottom:12px; }}
.topic-head {{ display:flex; justify-content:space-between; align-items:baseline;
  margin-bottom:6px; }}
.topic-name {{ font-weight:700; font-size:14px; letter-spacing:0.04em; }}
.topic-id {{ font-size:11px; color:var(--muted); font-family:ui-monospace,monospace; }}
.topic-purpose {{ font-size:13px; margin-bottom:3px; }}
.topic-content {{ font-size:12px; color:var(--muted); margin-bottom:8px; }}
code, .cmd {{ font-family:ui-monospace,"Cascadia Code",Consolas,monospace;
  font-size:11.5px; background:var(--surface2); border:1px solid var(--border);
  border-radius:5px; padding:2px 6px; color:var(--accent); }}
.cmd {{ display:block; padding:8px 10px; margin-top:6px; overflow-x:auto;
  white-space:nowrap; }}
table {{ width:100%; border-collapse:collapse; font-size:13px;
  background:var(--surface); border:1px solid var(--border); border-radius:10px;
  overflow:hidden; }}
th {{ text-align:left; font-size:11px; text-transform:uppercase;
  letter-spacing:0.06em; color:var(--muted); padding:10px 12px;
  border-bottom:1px solid var(--border); background:var(--surface2); }}
td {{ padding:9px 12px; border-bottom:1px solid var(--border); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.num {{ color:var(--muted); font-variant-numeric:tabular-nums; width:28px; }}
.score {{ font-variant-numeric:tabular-nums; font-weight:600; }}
.quote {{ color:var(--text); max-width:560px; }}
.small {{ font-size:12px; color:var(--muted); }}
.freq {{ font-size:12px; color:var(--muted); white-space:nowrap; }}
.tag {{ display:inline-block; font-size:10.5px; padding:2px 7px; border-radius:4px;
  background:var(--surface2); border:1px solid var(--border); color:var(--muted);
  white-space:nowrap; }}
.tag.fmt-short {{ color:var(--amber); border-color:#5a4415; }}
.tag.fmt-long {{ color:var(--blue); border-color:#1e3a5f; }}
a {{ color:var(--blue); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
footer {{ margin-top:36px; padding-top:16px; border-top:1px solid var(--border);
  font-size:12px; color:var(--muted); }}
.guard {{ background:#2a1a1a; border:1px solid #5c2626; border-radius:8px;
  padding:12px 16px; font-size:12.5px; color:#fca5a5; margin-top:12px; }}
.finding {{ background:var(--surface); border:1px solid var(--border);
  border-left:3px solid var(--muted); border-radius:8px;
  padding:12px 14px; margin-bottom:10px; }}
.finding.sev-critical {{ border-left-color:var(--red); }}
.finding.sev-high {{ border-left-color:#fb923c; }}
.finding.sev-medium {{ border-left-color:var(--amber); }}
.finding.sev-info {{ border-left-color:var(--blue); }}
.finding-head {{ display:flex; align-items:baseline; gap:9px; margin-bottom:5px; }}
.finding-body {{ font-size:12.5px; color:var(--muted); line-height:1.6; }}
.sev {{ font-size:10px; font-weight:700; letter-spacing:0.06em;
  padding:2px 7px; border-radius:4px; white-space:nowrap;
  background:var(--surface2); border:1px solid var(--border); }}
.sev.sev-critical {{ color:var(--red); border-color:#5c2626; }}
.sev.sev-high {{ color:#fb923c; border-color:#5c3a15; }}
.sev.sev-medium {{ color:var(--amber); border-color:#5a4415; }}
.sev.sev-info {{ color:var(--blue); border-color:#1e3a5f; }}
.tag-bot {{ display:inline-block; font-size:10px; font-weight:700;
  padding:2px 7px; border-radius:4px; color:var(--red);
  background:#2a1a1a; border:1px solid #5c2626; white-space:nowrap; }}
.note {{ font-size:11.5px; color:var(--muted); margin:-4px 0 10px; }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Azzam Ops Dashboard</h1>
  <div class="sub">@azzammastertradinggold • XAUUSD / Forex • English channel •
    cập nhật {now}</div>
</header>

<h2>Tình trạng hệ thống</h2>
<div class="stats">{stat_html}</div>

<h2>Analytics kênh mình — số liệu thật</h2>
<div class="note">{an_meta}</div>
<div class="stats">{an_html}</div>

<div class="grid2" style="margin-top:16px">
  <div class="card">
    <div style="font-size:13px;margin-bottom:8px"><strong>Nguồn traffic</strong></div>
    <table>
      <thead><tr><th>Nguồn</th><th>Views</th><th>Tỷ lệ</th><th>Watch</th></tr></thead>
      <tbody>{traffic_html}</tbody>
    </table>
  </div>
  <div class="card">
    <div style="font-size:13px;margin-bottom:8px"><strong>Nguồn ngoài (EXT_URL)</strong></div>
    <table>
      <thead><tr><th>Referrer</th><th>Views</th><th></th></tr></thead>
      <tbody>{ext_html}</tbody>
    </table>
  </div>
</div>

<h2>Điểm mù — phát hiện từ dữ liệu</h2>
<div class="note">{blind_meta}</div>
{blind_html}

<h2>Kiểm tra pipeline</h2>
<div class="grid2">
  <div class="card">
    <ul class="checks">{check_html}</ul>
  </div>
  <div class="card">
    <div style="font-size:13px;margin-bottom:8px"><strong>Luồng điều phối</strong></div>
    <div style="font-size:12.5px;color:var(--muted);line-height:1.7">
      Cào comment → chấm điểm pain → Alan duyệt ở topic <strong>COMMENT</strong>
      → gửi brief sang topic <strong>EDIT</strong> → editor dựng bằng CapCut MCP
      → QC → đăng → báo cáo về topic <strong>GENERAL</strong>.
    </div>
    <div class="guard">
      Guardrail: không cam kết lợi nhuận, không trade giả. Mọi lệnh gửi
      Telegram đều phải có <code>--approve APPROVE</code>. Editor không tự đăng.
    </div>
  </div>
</div>

<h2>Topic Telegram</h2>
{topic_html}

<h2>Pipeline 8 bước</h2>
<table>
  <thead><tr><th>#</th><th>Bước</th><th>Tool</th><th>Việc</th><th>Tần suất</th></tr></thead>
  <tbody>{pipe_html}</tbody>
</table>

<h2>Top pain point — chờ Alan duyệt</h2>
<table>
  <thead><tr><th>#</th><th>Nhóm</th><th>Score</th><th>Nội dung comment</th><th>Nguồn</th></tr></thead>
  <tbody>{pain_html}</tbody>
</table>

<h2>Content backlog — sẵn sàng cho editor</h2>
<table>
  <thead><tr><th>#</th><th>Format</th><th>Tiêu đề nháp</th><th>Pain cluster</th><th>CTA</th><th>Evidence</th></tr></thead>
  <tbody>{backlog_html}</tbody>
</table>

<footer>
  Sinh tự động từ dữ liệu thật trong repo. Không có số liệu nào được nhập tay.<br>
  Nguồn: YouTube Data API v3 (commentThreads, channels.list) + YouTube Analytics API
  (OAuth, private metrics) + phân tích pain point + strategy builder.<br>
  Chạy <code>python scripts/analyze_blindspots.py</code> để cập nhật phần điểm mù.
</footer>

</div>
</body>
</html>
"""

    path = OUT / "ops.html"
    path.write_text(html, encoding="utf-8")
    print(f"Written: {path.resolve()}")
    print(f"  size: {path.stat().st_size:,} bytes")
    print(f"  comments={len(comments)} pain={len(pain)} backlog={len(backlog)} "
          f"angles={len(angles)} mcp={'up' if mcp else 'down'}")
    print(f"  analytics={'yes' if analytics else 'no'} "
          f"blindspots={len((blind or {}).get('findings', []))}")
    print(f"  checks: {sum(1 for _,ok in checks if ok)}/{len(checks)} ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
