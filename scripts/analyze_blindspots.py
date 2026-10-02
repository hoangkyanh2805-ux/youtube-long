#!/usr/bin/env python3
"""Phân tích điểm mù từ số liệu YouTube Analytics thật.

Đọc `vendor/youtube-analytics-dashboard/analytics_latest.json` (private analytics
qua OAuth) + `history.csv` (public stats) → sinh báo cáo điểm mù có bằng chứng.

Mọi con số đều tính từ file thật. Không có số nào nhập tay, không suy diễn
ngoài dữ liệu. Chỉ số nào không tính được thì ghi rõ "không có data".

Phát hiện quan trọng mà script này bắt buộc phải kiểm:
  - traffic từ nguồn lạ (referrer bot: seofast, playbots...) = dấu hiệu view mua
  - tập trung view vào 1 ngày duy nhất = view không tự nhiên
  - tỷ lệ view/giây bất thường trên Shorts
  - sub conversion, comment rate thấp bất thường

Usage:
    python scripts/analyze_blindspots.py
    python scripts/analyze_blindspots.py --json outputs/reports/blindspots.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "youtube-analytics-dashboard"
OUT = ROOT / "outputs" / "reports"
OWNER_ID = "UCBZ7LaffmEPv91sWcfroJdQ"

# Referrer chứa các chuỗi này = nguồn traffic không tự nhiên (view farm / bot).
BOT_MARKERS = ("seofast", "playbot", "viewbot", "like4like", "sub4sub",
               "hits4pay", "trafficbot", "getviews", "youtubebot")


def load_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def load_csv(p: Path) -> list[dict]:
    if not p.exists():
        return []
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_int(v, d=0) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return d


def pct(n, d) -> float:
    return (n / d * 100) if d else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description="Phân tích điểm mù từ analytics thật.")
    ap.add_argument("--json", default=str(OUT / "blindspots.json"),
                    help="nơi ghi kết quả JSON")
    ap.add_argument("--md", default=str(OUT / "blindspots.md"),
                    help="nơi ghi báo cáo markdown")
    args = ap.parse_args()

    a = load_json(VENDOR / "analytics_latest.json")
    if not a:
        print("Thiếu analytics_latest.json — chạy scripts/refresh_youtube_analytics_dashboard.py trước.",
              file=sys.stderr)
        return 1

    m = a.get("metrics", {})
    views = to_int(m.get("views"))
    mins = to_int(m.get("estimatedMinutesWatched"))
    avg_dur = to_int(m.get("averageViewDuration"))
    avg_pct = float(m.get("averageViewPercentage") or 0)
    subs_g = to_int(m.get("subscribersGained"))
    subs_l = to_int(m.get("subscribersLost"))
    likes = to_int(m.get("likes"))
    shares = to_int(m.get("shares"))
    comments = to_int(m.get("comments"))
    daily = a.get("daily", [])
    traffic = a.get("traffic_sources", [])
    geo = a.get("geography", [])
    dev = a.get("devices", [])
    ext = a.get("external_urls", [])
    top = a.get("top_videos", [])

    findings = []   # (mức độ, tiêu đề, chi tiết, bằng chứng)

    def add(sev, title, detail, evidence):
        findings.append({"severity": sev, "title": title,
                         "detail": detail, "evidence": evidence})

    # ---- 1. Traffic từ nguồn lạ (bot/view farm) ----------------------------
    bot_rows = [r for r in ext if any(b in str(r[0]).lower() for b in BOT_MARKERS)]
    bot_views = sum(to_int(r[1]) for r in bot_rows)
    ext_total = sum(to_int(r[1]) for r in ext)
    if bot_rows:
        add("CRITICAL",
            f"Traffic từ nguồn nghi bot: {bot_views:,} views",
            f"{pct(bot_views, views):.1f}% tổng view 28 ngày đến từ referrer không phải "
            f"site thật. Đây là dấu hiệu view mua/view farm — YouTube có thể coi là "
            f"fake engagement và xoá view hoặc phạt kênh.",
            [{"source": r[0], "views": to_int(r[1])} for r in bot_rows])

    # ---- 2. View tập trung vào 1 ngày --------------------------------------
    if daily:
        peak = max(daily, key=lambda r: to_int(r[1]))
        peak_v = to_int(peak[1])
        nonzero = [to_int(r[1]) for r in daily if to_int(r[1]) > 0]
        med = sorted(nonzero)[len(nonzero) // 2] if nonzero else 0
        if views and pct(peak_v, views) > 50:
            add("CRITICAL",
                f"{pct(peak_v, views):.0f}% view dồn vào 1 ngày ({peak[0]})",
                f"Ngày {peak[0]} có {peak_v:,} view, trong khi trung vị các ngày còn lại "
                f"chỉ {med:,}. Phân bố này không tự nhiên với kênh organic — view tăng "
                f"đột biến rồi tắt ngay là dấu hiệu traffic mua, không phải nội dung viral.",
                [{"date": peak[0], "views": peak_v, "median_other_days": med}])

    # ---- 3. Traffic ngoài chiếm quá cao, search gần như bằng 0 -------------
    tv = {r[0]: to_int(r[1]) for r in traffic}
    total_t = sum(tv.values()) or views
    if tv.get("YT_SEARCH", 0) and pct(tv["YT_SEARCH"], total_t) < 3:
        add("HIGH",
            f"Tìm kiếm YouTube chỉ {pct(tv['YT_SEARCH'], total_t):.1f}% traffic",
            f"Kênh gần như không được tìm thấy trên YouTube ({tv['YT_SEARCH']:,} view). "
            f"Trong khi đó EXT_URL chiếm {pct(tv.get('EXT_URL',0), total_t):.0f}%. "
            f"Kênh đang phụ thuộc nguồn ngoài, không có discoverability tự nhiên — "
            f"không bền vững.",
            [{"source": k, "views": v, "pct": round(pct(v, total_t), 1)}
             for k, v in sorted(tv.items(), key=lambda x: -x[1])[:6]])

    # ---- 4. Subscriber conversion thấp ------------------------------------
    if views:
        conv = pct(subs_g, views)
        if conv < 0.5:
            add("HIGH",
                f"Sub conversion chỉ {conv:.3f}%",
                f"{subs_g} sub mới / {views:,} view. Mức tham chiếu ngành 0.5–2%. "
                f"Viewer xem nhưng không đăng ký — thiếu CTA hoặc nội dung không giữ chân.",
                [{"subs_gained": subs_g, "views": views, "conversion_pct": round(conv, 3)}])
        if subs_l >= subs_g:
            add("HIGH",
                f"Sub ròng âm: +{subs_g} / -{subs_l}",
                f"Kênh mất nhiều sub hơn được. Cần xem lại nội dung gần đây và tần suất đăng.",
                [{"gained": subs_g, "lost": subs_l, "net": subs_g - subs_l}])

    # ---- 5. Comment rate gần bằng 0 ---------------------------------------
    if views and comments is not None:
        cr = pct(comments, views)
        if cr < 0.05:
            add("HIGH",
                f"Comment rate {cr:.4f}% ({comments} comment / {views:,} view)",
                f"Tương tác bình luận gần như không có. Đây là chỉ số chết cho "
                f"thuật toán và cho phễu community. Like/comment = "
                f"{likes/max(comments,1):.0f}:1 (bình thường 20–50:1).",
                [{"comments": comments, "views": views,
                  "likes": likes, "like_per_comment": round(likes / max(comments, 1), 1)}])

    # ---- 6. Shorts: view nhưng không xem ---------------------------------
    shorts = next((r for r in traffic if r[0] == "SHORTS"), None)
    if shorts:
        sv, sm = to_int(shorts[1]), float(shorts[2] or 0)
        if sv and sm * 60 / sv < 5:
            add("MEDIUM",
                f"Shorts: {sm*60/sv:.1f} giây/view — view không thật",
                f"{sv:,} view Shorts nhưng chỉ {sm:,.0f} phút xem. View hợp lệ của "
                f"Shorts thường ≥10 giây. View bị tính nhưng người xem lướt qua ngay.",
                [{"views": sv, "watch_minutes": sm, "sec_per_view": round(sm*60/sv, 1)}])

    # ---- 7. Thời lượng xem trung bình quá ngắn ---------------------------
    if avg_dur and avg_pct and avg_pct < 1:
        implied_len_h = avg_dur / (avg_pct / 100) / 3600
        add("MEDIUM",
            f"View trung bình chỉ {avg_dur}s ({avg_pct}% video)",
            f"Người xem rời đi sau ~{avg_dur} giây. Nếu số này đúng thì độ dài video "
            f"trung bình ~{implied_len_h:.1f} giờ (livestream) — nghĩa là viewer chỉ xem "
            f"phần rất nhỏ. Hook và phần đầu video cần làm lại.",
            [{"avg_view_duration_s": avg_dur, "avg_view_pct": avg_pct,
              "implied_video_length_h": round(implied_len_h, 1)}])

    # ---- 8. Nội dung chỉ có 1 định dạng -----------------------------------
    live_count = sum(1 for v in top if "LIVE" in str(v[5]).upper())
    if top and live_count == len(top):
        add("MEDIUM",
            f"Top video 100% là livestream ({live_count}/{len(top)})",
            "Không có video dạng long-form biên tập hoặc Shorts trong top. "
            "Livestream khó lên đề xuất (không có thumbnail/SEO như video thường) "
            "và không tái sử dụng được. Kênh thiếu nội dung evergreen.",
            [{"top_video_count": len(top), "livestream_count": live_count}])

    # ---- 9. Địa lý lệch khỏi thị trường mục tiêu -------------------------
    if geo:
        gtotal = sum(to_int(r[1]) for r in geo)
        top_geo = geo[0]
        add("INFO",
            f"Top địa lý: {top_geo[0]} ({pct(to_int(top_geo[1]), gtotal):.0f}%)",
            "Kênh tiếng Anh nhưng cần kiểm tra tỷ trọng thị trường trả tiền cao "
            "(US/UK/CA/AU). Nếu phần lớn view đến từ thị trường RPM thấp, "
            "doanh thu sẽ thấp dù view cao.",
            [{"country": r[0], "views": to_int(r[1]),
              "pct": round(pct(to_int(r[1]), gtotal), 1)} for r in geo[:6]])

    # ---- 10. Mobile-first -----------------------------------------------
    if dev:
        dtotal = sum(to_int(r[1]) for r in dev)
        mob = next((to_int(r[1]) for r in dev if r[0] == "MOBILE"), 0)
        if pct(mob, dtotal) > 80:
            add("INFO",
                f"{pct(mob, dtotal):.0f}% view trên mobile",
                "Thumbnail, hook 3 giây đầu và phụ đề phải tối ưu cho màn hình dọc/nhỏ. "
                "Text nhỏ trên thumbnail gần như vô nghĩa với nhóm này.",
                [{"device": r[0], "views": to_int(r[1]),
                  "pct": round(pct(to_int(r[1]), dtotal), 1)} for r in dev])

    # ---- Số liệu nền ------------------------------------------------------
    hist = load_csv(VENDOR / "history.csv")
    latest_owner = None
    for r in hist:
        if r.get("channel_id") == OWNER_ID:
            if latest_owner is None or r.get("date", "") > latest_owner.get("date", ""):
                latest_owner = r

    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "window": {"start": a.get("start"), "end": a.get("end"), "days": a.get("days")},
        "metrics": m,
        "derived": {
            "watch_hours": round(mins / 60, 1),
            "sub_net": subs_g - subs_l,
            "sub_conversion_pct": round(pct(subs_g, views), 3),
            "like_rate_pct": round(pct(likes, views), 2),
            "comment_rate_pct": round(pct(comments, views), 4),
            "share_rate_pct": round(pct(shares, views), 3),
        },
        "bot_traffic": {"views": bot_views, "pct_of_channel": round(pct(bot_views, views), 1),
                        "sources": [{"source": r[0], "views": to_int(r[1])} for r in bot_rows]},
        "public_stats": latest_owner,
        "findings": findings,
    }

    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- Markdown ---------------------------------------------------------
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}
    findings.sort(key=lambda f: sev_order.get(f["severity"], 9))

    L = ["# Điểm mù kênh — phân tích từ dữ liệu thật", ""]
    L.append(f"*Sinh: {report['generated_at']}*  •  Cửa sổ: "
             f"{a.get('start')} → {a.get('end')} ({a.get('days')} ngày)")
    L.append("")
    L.append("Nguồn: YouTube Analytics API (OAuth, private metrics) + "
             "YouTube Data API v3 (public stats). Không có số liệu nhập tay.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Số liệu nền")
    L.append("")
    L.append("| Chỉ số | Giá trị |")
    L.append("|--------|---------|")
    L.append(f"| Views | {views:,} |")
    L.append(f"| Watch time | {report['derived']['watch_hours']:,} giờ |")
    L.append(f"| View trung bình | {avg_dur}s ({avg_pct}% video) |")
    L.append(f"| Sub | +{subs_g} / -{subs_l} = {report['derived']['sub_net']:+d} |")
    L.append(f"| Sub conversion | {report['derived']['sub_conversion_pct']}% |")
    L.append(f"| Like rate | {report['derived']['like_rate_pct']}% |")
    L.append(f"| Comment rate | {report['derived']['comment_rate_pct']}% |")
    L.append(f"| Share rate | {report['derived']['share_rate_pct']}% |")
    if latest_owner:
        L.append(f"| Tổng sub kênh | {to_int(latest_owner.get('subs')):,} |")
        L.append(f"| Tổng view kênh | {to_int(latest_owner.get('views')):,} |")
        L.append(f"| Số video | {to_int(latest_owner.get('videos')):,} |")
    L.append("")

    L.append("## Điểm mù phát hiện được")
    L.append("")
    L.append(f"Tổng: **{len(findings)}** "
             f"({sum(1 for f in findings if f['severity']=='CRITICAL')} critical, "
             f"{sum(1 for f in findings if f['severity']=='HIGH')} high, "
             f"{sum(1 for f in findings if f['severity']=='MEDIUM')} medium, "
             f"{sum(1 for f in findings if f['severity']=='INFO')} info)")
    L.append("")
    for i, f in enumerate(findings, 1):
        L.append(f"### {i}. [{f['severity']}] {f['title']}")
        L.append("")
        L.append(f["detail"])
        L.append("")
        L.append("Bằng chứng:")
        L.append("")
        L.append("```json")
        L.append(json.dumps(f["evidence"], ensure_ascii=False, indent=2))
        L.append("```")
        L.append("")

    Path(args.md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.md).write_text("\n".join(L), encoding="utf-8")

    # ---- Console ----------------------------------------------------------
    print(f"=== ĐIỂM MÙ — {a.get('start')} → {a.get('end')} ===")
    print(f"  views={views:,}  watch={report['derived']['watch_hours']}h  "
          f"subs={report['derived']['sub_net']:+d}  likes={likes:,}  comments={comments}")
    print(f"  bot traffic: {bot_views:,} views ({report['bot_traffic']['pct_of_channel']}% kênh)")
    print()
    for f in findings:
        print(f"  [{f['severity']:8}] {f['title']}")
    print()
    print(f"Written: {args.json}")
    print(f"Written: {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
