"""
Publish the dashboards into the dagu UI.

Two things get wired in:
  1. A Wiki page (`.dagu-local/dags/wiki/analytics.md`) with the REAL numbers
     pulled from the vendor dashboard's history.csv, plus clickable file links.
     dagu renders Wiki pages inside the UI, so the numbers are visible without
     leaving the browser.
  2. An `artifact.write` step in WF23 so each run carries the generated HTML
     as a downloadable artifact on the run page.

dagu cannot iframe a local file, so the HTML is surfaced as a link + artifact
rather than embedded. Everything else (numbers, links, timestamps) is in the UI.

Usage:
    python scripts/publish_dashboards_to_ui.py
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "youtube-analytics-dashboard"
WIKI = ROOT / ".dagu-local" / "dags" / "wiki"
DASH = ROOT / "outputs" / "dashboard"


def read_history() -> list[dict]:
    p = VENDOR / "history.csv"
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_analytics() -> dict | None:
    p = VENDOR / "analytics_latest.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def read_blindspots() -> dict | None:
    p = ROOT / "outputs" / "reports" / "blindspots.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def latest_per_channel(rows: list[dict]) -> dict[str, dict]:
    """Keep only the most recent snapshot per channel_id."""
    best: dict[str, dict] = {}
    for r in rows:
        cid = r.get("channel_id", "")
        if not cid:
            continue
        cur = best.get(cid)
        if cur is None or (r.get("date", "") > cur.get("date", "")):
            best[cid] = r
    return best


def to_int(v) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def fmt(n: int) -> str:
    return f"{n:,}"


def main() -> int:
    rows = read_history()
    latest = latest_per_channel(rows)
    if not latest:
        print("No history.csv rows — run scripts/refresh_youtube_analytics_dashboard.py first.",
              file=sys.stderr)
        return 1

    # Azzam is the owner channel; everything else is a competitor.
    owner_id = "UCBZ7LaffmEPv91sWcfroJdQ"
    owner = latest.get(owner_id)
    competitors = {k: v for k, v in latest.items() if k != owner_id}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append("# YouTube Analytics")
    lines.append("")
    lines.append(f"*Cập nhật: {now}*  •  Nguồn: YouTube Data API v3 "
                 f"(channels.list, statistics)")
    lines.append("")
    lines.append("---")
    lines.append("")

    if owner:
        lines.append("## Kênh mình")
        lines.append("")
        lines.append("| Chỉ số | Giá trị |")
        lines.append("|--------|---------|")
        lines.append(f"| Kênh | {owner.get('title','')} |")
        lines.append(f"| Subscribers | {fmt(to_int(owner.get('subs')))} |")
        lines.append(f"| Tổng views | {fmt(to_int(owner.get('views')))} |")
        lines.append(f"| Số video | {fmt(to_int(owner.get('videos')))} |")
        sub = to_int(owner.get("subs"))
        vid = to_int(owner.get("videos"))
        if vid:
            lines.append(f"| Views / video | {fmt(to_int(owner.get('views')) // vid)} |")
        lines.append(f"| Snapshot | {owner.get('date','')} |")
        lines.append("")

    if competitors:
        lines.append("## Đối thủ")
        lines.append("")
        lines.append("| Kênh | Subscribers | Tổng views | Video | Views/video |")
        lines.append("|------|------------|-----------|-------|-------------|")
        for cid, c in sorted(competitors.items(),
                             key=lambda kv: -to_int(kv[1].get("subs"))):
            v = to_int(c.get("videos"))
            vpv = to_int(c.get("views")) // v if v else 0
            lines.append(f"| {c.get('title','')} | {fmt(to_int(c.get('subs')))} | "
                         f"{fmt(to_int(c.get('views')))} | {fmt(v)} | {fmt(vpv)} |")
        lines.append("")

        if owner:
            os_ = to_int(owner.get("subs"))
            for cid, c in competitors.items():
                cs = to_int(c.get("subs"))
                if cs and os_:
                    gap = cs - os_
                    ratio = cs / os_
                    lines.append(f"- So với **{c.get('title','')}**: hơn "
                                 f"{fmt(gap)} sub ({ratio:.1f}×)")
            lines.append("")

    lines.append("## Dashboard (file local)")
    lines.append("")
    lines.append("dagu không nhúng được file HTML local vào UI, nên mở trực tiếp:")
    lines.append("")
    lines.append("- [Analytics dashboard (data thật)]"
                 "(file:///C:/Users/Admin/youtube/outputs/dashboard/youtube-analytics-real.html)")
    lines.append("- [Ops cockpit]"
                 "(file:///C:/Users/Admin/youtube/outputs/dashboard/ops.html)")
    lines.append("")
    lines.append("Mỗi lần chạy **WF23-publish-dashboards** trong UI, bản HTML mới nhất "
                 "được lưu thành artifact trên trang run đó.")
    lines.append("")

    # ---- Private analytics (OAuth) — số liệu chỉ chủ kênh thấy được -------
    a = read_analytics()
    if a:
        am = a.get("metrics", {})
        lines.append("## Analytics riêng tư (OAuth)")
        lines.append("")
        lines.append(f"*Cửa sổ {a.get('start')} → {a.get('end')} "
                     f"({a.get('days')} ngày) • YouTube Analytics API*")
        lines.append("")
        lines.append("| Chỉ số | Giá trị |")
        lines.append("|--------|---------|")
        lines.append(f"| Views | {fmt(to_int(am.get('views')))} |")
        lines.append(f"| Watch time | {to_int(am.get('estimatedMinutesWatched'))/60:,.1f} giờ |")
        lines.append(f"| View trung bình | {to_int(am.get('averageViewDuration'))}s "
                     f"({am.get('averageViewPercentage')}% video) |")
        lines.append(f"| Sub | +{to_int(am.get('subscribersGained'))} / "
                     f"-{to_int(am.get('subscribersLost'))} |")
        lines.append(f"| Likes / Shares / Comments | {fmt(to_int(am.get('likes')))} / "
                     f"{fmt(to_int(am.get('shares')))} / {to_int(am.get('comments'))} |")
        lines.append("")

        ts = a.get("traffic_sources", [])
        if ts:
            tot = sum(to_int(r[1]) for r in ts) or 1
            lines.append("### Nguồn traffic")
            lines.append("")
            lines.append("| Nguồn | Views | Tỷ lệ | Watch (min) |")
            lines.append("|-------|-------|-------|-------------|")
            for r in ts[:8]:
                v = to_int(r[1])
                lines.append(f"| {r[0]} | {fmt(v)} | {v/tot*100:.1f}% | "
                             f"{to_int(r[2]):,} |")
            lines.append("")

        ex = a.get("external_urls", [])
        if ex:
            lines.append("### Nguồn ngoài (EXT_URL) — kiểm tra bot")
            lines.append("")
            lines.append("| Referrer | Views | Cảnh báo |")
            lines.append("|----------|-------|----------|")
            BOT = ("seofast", "playbot", "viewbot", "like4like", "sub4sub")
            for r in ex[:10]:
                flag = "**NGHI BOT**" if any(b in str(r[0]).lower() for b in BOT) else ""
                lines.append(f"| {r[0]} | {fmt(to_int(r[1]))} | {flag} |")
            lines.append("")

    # ---- Điểm mù ---------------------------------------------------------
    b = read_blindspots()
    if b:
        fs = b.get("findings", [])
        lines.append("## Điểm mù phát hiện được")
        lines.append("")
        lines.append(f"*{len(fs)} phát hiện • sinh {b.get('generated_at','')}*")
        lines.append("")
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}
        for f in sorted(fs, key=lambda x: sev_order.get(x.get("severity"), 9)):
            lines.append(f"- **[{f.get('severity')}]** {f.get('title')}")
        lines.append("")
        lines.append("Chi tiết + bằng chứng: "
                     "[blindspots.md](file:///C:/Users/Admin/youtube/outputs/reports/blindspots.md)")
        lines.append("")

    lines.append("## Lịch sử snapshot")
    lines.append("")
    lines.append("| Ngày | Kênh | Subs | Views | Video |")
    lines.append("|------|------|------|-------|-------|")
    for r in sorted(rows, key=lambda x: (x.get("date", ""), x.get("title", "")),
                    reverse=True)[:20]:
        lines.append(f"| {r.get('date','')} | {r.get('title','')} | "
                     f"{fmt(to_int(r.get('subs')))} | {fmt(to_int(r.get('views')))} | "
                     f"{fmt(to_int(r.get('videos')))} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Cách chạy")
    lines.append("")
    lines.append("```")
    lines.append("# Cập nhật số liệu + đẩy vào artifact")
    lines.append("Bấm WF23-publish-dashboards trong UI, hoặc:")
    lines.append("python scripts/publish_dashboards_to_ui.py")
    lines.append("```")
    lines.append("")

    WIKI.mkdir(parents=True, exist_ok=True)
    out = WIKI / "analytics.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    print(f"Written: {out}")
    print(f"  owner: {owner.get('title') if owner else 'n/a'} "
          f"({fmt(to_int(owner.get('subs'))) if owner else 0} subs)")
    print(f"  competitors: {len(competitors)}")
    print(f"  history rows: {len(rows)}")

    # also drop a JSON snapshot the dashboard/WF23 can reuse
    snap = DASH / "analytics_snapshot.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    snap.write_text(json.dumps({
        "generated_at": now,
        "owner": owner,
        "competitors": competitors,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {snap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
