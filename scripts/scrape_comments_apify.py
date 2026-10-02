#!/usr/bin/env python3
"""CÀO COMMENT ĐA NỀN TẢNG lấy pain point — YouTube / TikTok / Instagram / Facebook.

Alan yêu cầu (thread 13 msg 1330, 1388):
  "thêm tool Apify cào comment youtube, tiktok, social để lấy pain point"

Dùng Apify MCP actors (đã cấu hình trong scripts/apify_mcp_launcher.py):
  streamers/youtube-comments-scraper      — YouTube
  clockworks/tiktok-comments-scraper      — TikTok
  apify/instagram-comment-scraper         — Instagram
  apify/facebook-comments-scraper         — Facebook

Chi phí: đo thật bằng usageTotalUsd. Free plan $5/tháng.
  YouTube: ~$0/run cho tới hàng nghìn comment (đã test: 40 comment = $0.0000)
  Kiểm tra số dư trước khi chạy batch lớn.

Nguyên tắc:
  - Lọc comment của chính chủ kênh (authorIsChannelOwner) — không tính vào pain point.
  - Không tự đăng/bình luận. Chỉ ĐỌC (read-only).
  - Ghi rõ nguồn: platform, video, tác giả, ngày để audit trail.
  - Kết quả vào outputs/painpoints/<run>/ để không ghi đè lần chạy trước.

Usage:
    python scripts/scrape_comments_apify.py --platform youtube --urls URL1 URL2
    python scripts/scrape_comments_apify.py --platform youtube --from-competitor
    python scripts/scrape_comments_apify.py --balance
    python scripts/scrape_comments_apify.py --dry-run --platform tiktok --urls X

Xuất:
    outputs/painpoints/<run_id>/raw_comments.json
    outputs/painpoints/<run_id>/comments.csv
    outputs/painpoints/<run_id>/run_metadata.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "painpoints"
ENV_FILES = (ROOT / ".env",
             Path.home() / "AppData/Local/hermes/profiles/youtube/.env")

ACTORS = {
    "youtube": "streamers~youtube-comments-scraper",
    "tiktok": "clockworks~tiktok-comments-scraper",
    "instagram": "apify~instagram-comment-scraper",
    "facebook": "apify~facebook-comments-scraper",
}

# Tên tham số khác nhau giữa các actor — phải khai đúng, sai sẽ FAILED
# với "You need to provide either searchQueries or startUrls as input".
INPUT_SHAPE = {
    "youtube": ("startUrls", lambda urls: [{"url": u} for u in urls]),
    "tiktok": ("postURLs", lambda urls: urls),
    "instagram": ("directUrls", lambda urls: urls),
    "facebook": ("startUrls", lambda urls: [{"url": u} for u in urls]),
}


def read_env(key: str) -> str:
    v = os.environ.get(key, "").strip()
    if v:
        return v
    for p in ENV_FILES:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def api(path: str, token: str, data: dict | None = None, timeout: int = 90):
    url = f"https://api.apify.com/v2{path}"
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}token={urllib.parse.quote(token)}"
    if data is None:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
    else:
        req = urllib.request.Request(
            url, data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_err": e.code, "_body": e.read().decode("utf-8", "replace")[:400]}
    except Exception as e:
        return {"_err": type(e).__name__, "_body": str(e)[:200]}


def show_balance(token: str) -> int:
    d = api("/users/me", token)
    if "_err" in d:
        print(f"✗ Không đọc được tài khoản: {d['_err']} {d.get('_body','')}")
        return 1
    u = d.get("data", {})
    print(f"  Tài khoản : {u.get('username')}")
    print(f"  Plan      : {u.get('plan', {}).get('id') if isinstance(u.get('plan'), dict) else u.get('plan')}")

    lim = api("/users/me/limits", token)
    if "_err" not in lim:
        cur = lim.get("data", {}).get("current", {})
        used = cur.get("monthlyUsageUsd", 0)
        cyc = cur.get("monthlyUsageCycle") or {}
        cap = cyc.get("limitUsd") if isinstance(cyc, dict) else None
        print(f"  Đã dùng   : ${used:.4f}" + (f" / ${cap:.2f}" if cap else ""))
        if cap:
            print(f"  Còn lại   : ${cap - used:.4f}")
    return 0


def competitor_videos(limit: int = 5) -> list[str]:
    """Lấy video đối thủ có nhiều comment nhất từ data đã cào."""
    p = ROOT / "outputs/competitor_longform/painpoint_candidates.csv"
    if not p.exists():
        return []
    seen, out = set(), []
    with p.open(encoding="utf-8-sig", newline="") as f:
        rows = sorted(csv.DictReader(f),
                      key=lambda r: -(int(float(r.get("engagement_likes") or 0))))
    for r in rows:
        u = str(r.get("content_url", ""))
        if "watch?v=" in u:
            vid = u.split("watch?v=")[1].split("&")[0]
            if vid not in seen:
                seen.add(vid)
                out.append(f"https://www.youtube.com/watch?v={vid}")
        if len(out) >= limit:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--platform", choices=list(ACTORS), default="youtube")
    ap.add_argument("--urls", nargs="*", default=[])
    ap.add_argument("--from-competitor", action="store_true",
                    help="lấy URL video đối thủ từ data đã cào")
    ap.add_argument("--limit", type=int, default=5, help="số video khi --from-competitor")
    ap.add_argument("--max-comments", type=int, default=100)
    ap.add_argument("--balance", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--poll-timeout", type=int, default=900)
    args = ap.parse_args()

    token = read_env("APIFY_TOKEN")
    if not token:
        print("✗ Thiếu APIFY_TOKEN. Thêm vào .env (xem .env.example).", file=sys.stderr)
        return 2

    if args.balance:
        return show_balance(token)

    urls = list(args.urls)
    if args.from_competitor:
        urls += competitor_videos(args.limit)
    urls = [u for u in dict.fromkeys(urls) if u]
    if not urls:
        print("✗ Chưa có URL. Dùng --urls ... hoặc --from-competitor", file=sys.stderr)
        return 2

    actor = ACTORS[args.platform]
    key, shaper = INPUT_SHAPE[args.platform]
    payload = {key: shaper(urls), "maxComments": args.max_comments}

    print(f"Nền tảng : {args.platform}")
    print(f"Actor    : {actor}")
    print(f"URL      : {len(urls)}")
    for u in urls[:5]:
        print(f"           {u}")
    print(f"Tối đa   : {args.max_comments} comment/URL")
    print(f"Payload  : {key}=…")

    if args.dry_run:
        print("\n(dry-run — không gọi API)")
        return 0

    show_balance(token)
    print()

    r = api(f"/acts/{actor}/runs", token, data=payload)
    if "_err" in r:
        print(f"✗ Không start được run: {r['_err']} {r.get('_body','')}")
        return 1
    run = r["data"]
    rid = run["id"]
    print(f"▶ Run: {rid}  status={run['status']}")

    deadline = time.time() + args.poll_timeout
    status = run["status"]
    ds = None
    usage = 0.0
    while time.time() < deadline:
        time.sleep(10)
        st = api(f"/actor-runs/{rid}", token)
        if "_err" in st:
            print(f"  poll lỗi: {st['_err']}")
            continue
        d = st["data"]
        status = d["status"]
        print(f"  [{int(time.time() - (deadline - args.poll_timeout))}s] {status}")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            ds = d.get("defaultDatasetId")
            usage = d.get("usageTotalUsd", 0) or 0
            break

    if status != "SUCCEEDED":
        print(f"\n✗ Run kết thúc với status={status} (chi phí ${usage:.4f})")
        log = api(f"/actor-runs/{rid}/log", token, timeout=60)
        if isinstance(log, str):
            print(log[-1200:])
        return 1

    items = []
    if ds:
        it = api(f"/datasets/{ds}/items?limit=100000", token, timeout=120)
        items = it if isinstance(it, list) else it.get("data", [])
    print(f"\n✓ {len(items):,} comment · chi phí ${usage:.4f}")

    # ── Ghi kết quả ─────────────────────────────────────────────────────────
    run_id = f"apify_{args.platform}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    d = OUT / run_id
    d.mkdir(parents=True, exist_ok=True)

    (d / "raw_comments.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # Chuẩn hoá về schema dùng chung (giống painpoint_candidates.csv cũ)
    rows = []
    for it in items:
        txt = (it.get("comment") or it.get("text") or "").strip()
        if not txt:
            continue
        rows.append({
            "platform": args.platform,
            "comment_text": txt,
            "author": it.get("author", ""),
            "author_is_channel_owner": bool(it.get("authorIsChannelOwner")),
            "engagement_likes": it.get("voteCount") or it.get("likesCount") or 0,
            "reply_count": it.get("replyCount") or 0,
            "content_url": it.get("pageUrl") or it.get("url") or "",
            "video_title": it.get("title", ""),
            "comment_id": it.get("cid") or it.get("id") or "",
            "published": it.get("publishedTimeText", ""),
        })

    # Lọc comment của chính chủ kênh — không tính vào pain point khán giả
    before = len(rows)
    rows = [r for r in rows if not r["author_is_channel_owner"]]
    removed = before - len(rows)

    csv_path = d / "comments.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ["platform", "comment_text"])
        w.writeheader()
        w.writerows(rows)

    meta = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": args.platform,
        "actor": actor,
        "apify_run_id": rid,
        "apify_dataset_id": ds,
        "cost_usd": round(usage, 4),
        "urls": urls,
        "max_comments_per_url": args.max_comments,
        "raw_items": len(items),
        "kept_after_filter": len(rows),
        "removed_channel_owner": removed,
        "note": "Read-only. Comment của chính chủ kênh đã bị loại khỏi dữ liệu.",
    }
    (d / "run_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  ✓ {csv_path.relative_to(ROOT)}  ({len(rows):,} dòng)")
    print(f"  ✓ raw_comments.json ({len(items):,})")
    print(f"  ✓ run_metadata.json")
    if removed:
        print(f"  ℹ đã loại {removed} comment của chính chủ kênh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
