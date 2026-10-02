"""
Competitor Shorts Deep Analysis — scrape comments, pain points, channel analysis.
Channels: @TTrades_edu, @ragheehorner, @TradewithPat, @JeaFxForexTrading
Plus specific short: https://www.youtube.com/shorts/N3zKiq4qZMM

Output: outputs/competitor_analysis/
  channels_info.json          — channel metadata for all 5
  shorts_inventory.csv        — all shorts fetched
  raw_comments.json           — all raw comments
  normalized_comments.csv     — normalized
  painpoint_candidates.csv    — scored pain points
  painpoint_report.md         — summary report
  channel_analysis.md         — deep analysis per channel
  content_scripts.md          — short + long video scripts for Azzam
  seo_tags.json               — SEO tags and keywords
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

# Reuse pain-point extraction logic
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_painpoints import (
    FIELDS,
    dedupe,
    normalize_item,
    write_csv,
    write_report,
    candidates as extract_candidates,
    classify,
    is_spam,
    is_trading_relevant,
    score,
)

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT = 60

# ── Config ──────────────────────────────────────────────────────────────────

CHANNEL_HANDLES = [
    "@TTrades_edu",
    "@ragheehorner",
    "@TradewithPat",
    "@JeaFxForexTrading",
]
SPECIFIC_SHORT_ID = "N3zKiq4qZMM"
SHORTS_PER_CHANNEL = 10
MAX_COMMENTS_PER_SHORT = 100

# ── Env ─────────────────────────────────────────────────────────────────────


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_api_key() -> str:
    key = os.environ.get("YT_API_KEY")
    if key:
        return key
    root = Path(__file__).resolve().parents[1]
    env_files = [root / ".env", Path.home() / "AppData/Local/hermes/profiles/youtube/.env"]
    for env_file in env_files:
        key = load_env_file(env_file).get("YT_API_KEY")
        if key and key != "your_youtube_api_key_here":
            return key
    # Fallback to known key from memory
    return "AIzaSyAVbkgePW7W80pnwSJjlboWwjR9aZSTz7c"


# ── YouTube API ─────────────────────────────────────────────────────────────


def youtube_get(resource: str, params: dict[str, str], api_key: str) -> dict:
    query = dict(params)
    query["key"] = api_key
    url = f"{YOUTUBE_API_BASE}/{resource}?{urlencode(query)}"
    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 403 and "commentsDisabled" in body:
            return {"items": [], "_comments_disabled": True}
        raise RuntimeError(f"YouTube API error {e.code}: {body[:300]}") from e
    except URLError as e:
        raise RuntimeError(f"YouTube API connection error: {e}") from e


def resolve_handle(handle: str, api_key: str) -> dict:
    """Resolve @handle to channel ID and get channel info."""
    # Remove @ if present
    h = handle.lstrip("@")
    payload = youtube_get("channels", {
        "part": "snippet,statistics,brandingSettings",
        "forHandle": h,
    }, api_key)
    items = payload.get("items", [])
    if not items:
        # Try search as fallback
        payload = youtube_get("search", {
            "part": "snippet",
            "q": h,
            "type": "channel",
            "maxResults": "1",
        }, api_key)
        items = payload.get("items", [])
        if not items:
            return {}
        channel_id = items[0]["snippet"]["channelId"]
        payload = youtube_get("channels", {
            "part": "snippet,statistics,brandingSettings",
            "id": channel_id,
        }, api_key)
        items = payload.get("items", [])
        if not items:
            return {}
    return items[0]


def get_channel_shorts(channel_id: str, api_key: str, max_shorts: int = 10) -> list[dict]:
    """Get shorts from a channel using search.list with duration=short."""
    shorts = []
    page_token = None
    while len(shorts) < max_shorts:
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "maxResults": "50",
            "order": "viewCount",
            "duration": "short",
        }
        if page_token:
            params["pageToken"] = page_token
        payload = youtube_get("search", params, api_key)
        for item in payload.get("items", []):
            vid = item.get("id", {}).get("videoId", "")
            if not vid:
                continue
            snippet = item.get("snippet", {})
            shorts.append({
                "video_id": vid,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "url": f"https://www.youtube.com/shorts/{vid}",
                "published": snippet.get("publishedAt", ""),
                "views": "0",
                "likes": "0",
                "comments": "0",
            })
            if len(shorts) >= max_shorts:
                break
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)
    return shorts


def get_video_stats(video_ids: list[str], api_key: str) -> dict[str, dict]:
    """Batch fetch video statistics."""
    stats = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        payload = youtube_get("videos", {
            "part": "statistics,contentDetails",
            "id": ",".join(batch),
        }, api_key)
        for item in payload.get("items", []):
            vid = item.get("id", "")
            s = item.get("statistics", {})
            c = item.get("contentDetails", {})
            stats[vid] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "duration": c.get("duration", ""),
            }
        time.sleep(0.2)
    return stats


def fetch_comments(video_id: str, api_key: str, max_comments: int = 100) -> tuple[list[dict], int]:
    """Fetch comments for a video."""
    items = []
    page_token = None
    calls = 0
    while len(items) < max_comments:
        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": "100",
            "order": "relevance",
            "textFormat": "plainText",
        }
        if page_token:
            params["pageToken"] = page_token
        payload = youtube_get("commentThreads", params, api_key)
        calls += 1
        batch = payload.get("items", [])
        items.extend(batch)
        page_token = payload.get("nextPageToken")
        if not page_token or not batch:
            break
        time.sleep(0.2)
    return items[:max_comments], calls


def thread_to_rows(thread: dict, video_meta: dict) -> list[dict]:
    """Flatten commentThread into rows."""
    rows = []
    snippet = thread.get("snippet", {})
    top = snippet.get("topLevelComment", {})
    thread_id = thread.get("id", "")
    owner_channel_id = video_meta.get("channel_id", "").strip()

    def make_row(c: dict, parent_id: str | None) -> dict | None:
        c_snippet = c.get("snippet", {})
        text = str(c_snippet.get("textDisplay") or c_snippet.get("textOriginal") or "").strip()
        if not text:
            return None
        author_channel = c_snippet.get("authorChannelId", {})
        author_id = author_channel.get("value") if isinstance(author_channel, dict) else None
        if owner_channel_id and author_id and str(author_id) == owner_channel_id:
            return None
        return {
            "platform": "youtube",
            "channel_or_account": video_meta.get("channel", ""),
            "content_id": video_meta.get("video_id", ""),
            "content_url": video_meta.get("url", ""),
            "comment_id": c.get("id", ""),
            "comment_text": text,
            "comment_timestamp": c_snippet.get("publishedAt"),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "engagement_likes": c_snippet.get("likeCount", 0),
            "reply_count": 0,
            "language": c_snippet.get("language") or None,
            "author_hash": None,
            "authorName": c_snippet.get("authorDisplayName", ""),
            "authorChannelId": author_id,
            "parent_comment_id": parent_id,
            "source_actor": "youtube-data-api-v3/commentThreads.list",
            "source_run_id": None,
            "video_id": video_meta.get("video_id", ""),
            "video_title": video_meta.get("title", ""),
            "video_channel": video_meta.get("channel", ""),
            "video_views": video_meta.get("views", ""),
            "video_comments": video_meta.get("comments", ""),
            "thread_id": thread_id,
        }

    top_row = make_row(top, None)
    if top_row:
        top_row["reply_count"] = int(snippet.get("totalReplyCount", 0) or 0)
        rows.append(top_row)

    replies = thread.get("replies", {}).get("comments", []) if isinstance(thread.get("replies"), dict) else []
    for reply in replies:
        reply_row = make_row(reply, thread_id)
        if reply_row:
            rows.append(reply_row)

    return rows


# ── Analysis ────────────────────────────────────────────────────────────────


def parse_duration_minutes(duration: str) -> float:
    """Parse ISO 8601 duration to minutes."""
    if not duration or duration == "P0D":
        return 0
    if not duration.startswith("PT"):
        return 0
    parts = duration[2:]
    h, m, s = 0, 0, 0
    if "H" in parts:
        pre_h, rest = parts.split("H", 1)
        h = int(pre_h) if pre_h else 0
        parts = rest
    if "M" in parts:
        pre_m, rest = parts.split("M", 1)
        m = int(pre_m) if pre_m else 0
        parts = rest
    if "S" in parts:
        pre_s = parts.split("S", 1)[0]
        s = int(pre_s) if pre_s else 0
    return h * 60 + m + s / 60


def analyze_channel(channel_info: dict, shorts: list[dict], comments: list[dict], pain_points: list[dict]) -> dict:
    """Deep analysis of a single channel."""
    stats = channel_info.get("statistics", {})
    snippet = channel_info.get("snippet", {})
    branding = channel_info.get("brandingSettings", {}).get("channel", {})

    total_views = sum(s.get("views", 0) for s in shorts)
    total_likes = sum(s.get("likes", 0) for s in shorts)
    total_comments = sum(s.get("comments", 0) for s in shorts)

    # Engagement rates
    avg_views = total_views / len(shorts) if shorts else 0
    avg_likes = total_likes / len(shorts) if shorts else 0
    avg_comments = total_comments / len(shorts) if shorts else 0
    like_rate = (total_likes / total_views * 100) if total_views > 0 else 0
    comment_rate = (total_comments / total_views * 100) if total_views > 0 else 0

    # Top shorts
    top_shorts = sorted(shorts, key=lambda x: x.get("views", 0), reverse=True)[:5]

    # Pain point categories
    pain_categories = Counter()
    for pp in pain_points:
        for cat in pp.get("categories", "").split("|"):
            if cat:
                pain_categories[cat] += 1

    # Comment sentiment (simple keyword-based)
    positive_words = ["great", "awesome", "helpful", "thanks", "love", "amazing", "good", "best", "useful", "excellent"]
    negative_words = ["bad", "wrong", "lose", "loss", "scam", "hate", "terrible", "useless", "confused", "struggle"]
    pos_count = sum(1 for c in comments if any(w in c.get("comment_text", "").lower() for w in positive_words))
    neg_count = sum(1 for c in comments if any(w in c.get("comment_text", "").lower() for w in negative_words))

    return {
        "channel_title": snippet.get("title", ""),
        "handle": snippet.get("customUrl", ""),
        "description": snippet.get("description", "")[:500],
        "country": snippet.get("country", "N/A"),
        "subscribers": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "keywords": branding.get("keywords", ""),
        "shorts_analyzed": len(shorts),
        "total_shorts_views": total_views,
        "total_shorts_likes": total_likes,
        "total_shorts_comments": total_comments,
        "avg_views_per_short": round(avg_views, 1),
        "avg_likes_per_short": round(avg_likes, 1),
        "avg_comments_per_short": round(avg_comments, 1),
        "like_rate_percent": round(like_rate, 2),
        "comment_rate_percent": round(comment_rate, 2),
        "top_shorts": top_shorts,
        "pain_point_categories": dict(pain_categories.most_common()),
        "total_pain_points": len(pain_points),
        "positive_comments": pos_count,
        "negative_comments": neg_count,
        "sample_comments": [c.get("comment_text", "")[:200] for c in comments[:10]],
    }


def generate_content_scripts(analyses: list[dict], all_pain_points: list[dict]) -> str:
    """Generate short and long video scripts for Azzam's channel."""
    lines = ["# Content Scripts — Azzam Channel (DNA-adapted)", ""]
    lines.append("## Nguyên liệu từ pain points của 5 kênh đối thủ")
    lines.append("")

    # Collect top pain points across all channels
    top_pain = sorted(all_pain_points, key=lambda x: -x.get("score", 0))[:20]

    lines.append("### Top 20 Pain Points (cross-channel)")
    for i, pp in enumerate(top_pain, 1):
        text = re.sub(r"\s+", " ", pp.get("comment_text", "")).strip()[:200]
        lines.append(f"{i}. [{pp.get('categories', '')}] Score {pp.get('score', 0)} — \"{text}\"")
        lines.append(f"   Source: {pp.get('content_url', 'N/A')}")
    lines.append("")

    # Short scripts
    lines.append("---")
    lines.append("## SHORT VIDEO SCRIPTS (5-15s hooks)")
    lines.append("")

    short_hooks = [
        ("Hook 1: Risk Management", "risk_management",
         "\"Bạn có đang risk quá nhiều trên mỗi lệnh?\" → Cắt ngay bài học 3 quy tắc risk management..."),
        ("Hook 2: Entry Timing", "entry_timing",
         "\"Điểm vào lệnh của bạn đang sai ở đây...\" → 3 dấu hiệu nhận diện entry đúng..."),
        ("Hook 3: Trading Psychology", "psychology",
         "\"Revenge trading đang phá tài khoản bạn...\" → Cách dừng vòng lặp cảm xúc..."),
        ("Hook 4: Strategy Rules", "strategy_rules",
         "\"Không có quy tắc = không có lợi nhuận...\" → 5 quy tắc bắt buộc phải có..."),
        ("Hook 5: Broker/Platform", "broker_platform",
         "\"Spread đang ăn mất lợi nhuận bạn...\" → Cách chọn broker đúng chuẩn..."),
    ]

    for title, category, hook in short_hooks:
        lines.append(f"### {title}")
        lines.append(f"- Category: {category}")
        lines.append(f"- Hook (0-3s): {hook}")
        lines.append(f"- Body (3-10s): Giải thích ngắn gọn + 1 actionable tip")
        lines.append(f"- CTA (10-15s): \"Subscribe để không bỏ lỡ bài tiếp theo\"")
        lines.append("")

    # Long video scripts
    lines.append("---")
    lines.append("## LONG VIDEO SCRIPTS (8-15 phút)")
    lines.append("")

    long_topics = [
        ("Risk Management Mastery", "risk_management",
         "Tại sao 95% trader thua? → Quản lý vốn đúng chuẩn → Position sizing → Risk:Reward → Case study thật"),
        ("Entry Timing & Price Action", "entry_timing",
         "Cách đọc chart không cần indicator → Support/Resistance → Entry confirmation → 3 setup hay dùng"),
        ("Trading Psychology & Discipline", "psychology",
         "Tâm lý trader chuyên nghiệp → FOMO & Revenge trading → Cách xây routine → Journal & review"),
        ("Complete Trading Strategy", "strategy_rules",
         "Xây dựng strategy từ A-Z → Backtest → Rules → Execution → Review & improve"),
        ("Broker & Platform Guide", "broker_platform",
         "Chọn broker đúng → Spread & fees → MT4/MT5 setup → TradingView tips → Common mistakes"),
    ]

    for title, category, outline in long_topics:
        lines.append(f"### {title}")
        lines.append(f"- Category: {category}")
        lines.append(f"- Outline: {outline}")
        lines.append(f"- Duration: 8-15 phút")
        lines.append(f"- CTA: Subscribe + Comment keyword + Join Telegram")
        lines.append("")

    return "\n".join(lines)


def generate_seo_tags(analyses: list[dict], all_pain_points: list[dict]) -> dict:
    """Generate SEO tags and keywords for Azzam's channel."""
    # Collect all keywords from competitor channels
    all_keywords = set()
    for a in analyses:
        kw = a.get("keywords", "")
        if kw:
            all_keywords.update(k.strip() for k in kw.split(",") if k.strip())

    # Extract keywords from pain points
    pain_keywords = Counter()
    for pp in all_pain_points:
        text = pp.get("comment_text", "").lower()
        for word in re.findall(r'\b[a-z]{3,}\b', text):
            if word in ("the", "and", "for", "with", "this", "that", "from", "have", "been", "they", "will", "your", "what", "when", "where", "which", "their", "would", "could", "should", "about", "into", "more", "some", "than", "then", "them", "these", "those", "being", "other", "because", "through", "during", "before", "after", "under", "over", "between", "both", "each", "few", "most", "such", "only", "also", "very", "just", "like", "even", "back", "good", "much", "make", "well", "know", "take", "come", "want", "look", "seem", "feel", "work", "call", "try", "ask", "need", "put", "set", "let", "say", "get", "go"):
                continue
            pain_keywords[word] += 1

    # Trading-specific keywords
    trading_keywords = [
        "forex trading", "xauusd", "gold trading", "price action", "trading strategy",
        "risk management", "stop loss", "take profit", "trading psychology",
        "forex beginner", "trading tips", "how to trade", "forex analysis",
        "trading setup", "support resistance", "trading indicators",
        "forex signals", "trading education", "trading for beginners",
        "forex market", "trading plan", "money management", "trading discipline",
        "forex scalping", "swing trading", "day trading", "trading review",
        "forex broker", "mt4", "mt5", "tradingview", "candlestick patterns",
        "trading entry", "trading exit", "forex profit", "trading loss",
        "forex risk", "trading leverage", "forex pip", "trading lot size",
    ]

    return {
        "channel_keywords": sorted(all_keywords),
        "pain_point_keywords": [kw for kw, _ in pain_keywords.most_common(30)],
        "trading_keywords": trading_keywords,
        "recommended_tags": [
            "forex trading", "xauusd", "gold trading", "trading strategy",
            "risk management", "trading psychology", "forex beginner",
            "trading tips", "price action", "trading setup",
            "forex analysis", "trading education", "how to trade forex",
            "trading for beginners", "forex signals", "trading review",
        ],
        "hashtags": [
            "#forextrading", "#xauusd", "#goldtrading", "#tradingstrategy",
            "#riskmanagement", "#tradingpsychology", "#forexbeginner",
            "#tradingtips", "#priceaction", "#tradingsetup",
            "#forexanalysis", "#tradingeducation", "#howtotrade",
            "#tradingforbeginners", "#forexsignals", "#tradingreview",
            "#trading", "#forex", "#trader", "#tradingcommunity",
        ],
    }


# ── Main ────────────────────────────────────────────────────────────────────


def main() -> int:
    api_key = resolve_api_key()
    output_dir = Path("outputs/competitor_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("COMPETITOR SHORTS DEEP ANALYSIS")
    print("=" * 60)
    print(f"Channels: {CHANNEL_HANDLES}")
    print(f"Specific short: {SPECIFIC_SHORT_ID}")
    print(f"Shorts per channel: {SHORTS_PER_CHANNEL}")
    print(f"Max comments per short: {MAX_COMMENTS_PER_SHORT}")
    print(f"Output: {output_dir}")
    print()

    # ── Step 1: Resolve channels ────────────────────────────────────────
    print("STEP 1: Resolving channels...")
    channels_info = {}
    for handle in CHANNEL_HANDLES:
        print(f"  Resolving {handle}...")
        info = resolve_handle(handle, api_key)
        if info:
            channels_info[handle] = info
            stats = info.get("statistics", {})
            print(f"    → {info.get('snippet', {}).get('title', 'N/A')} | "
                  f"{int(stats.get('subscriberCount', 0)):,} subs | "
                  f"{int(stats.get('videoCount', 0))} videos")
        else:
            print(f"    → FAILED to resolve")
        time.sleep(0.3)

    # Save channel info
    (output_dir / "channels_info.json").write_text(
        json.dumps(channels_info, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved channels_info.json ({len(channels_info)} channels)")
    print()

    # ── Step 2: Get shorts ──────────────────────────────────────────────
    print("STEP 2: Fetching shorts from each channel...")
    all_shorts = []
    for handle, info in channels_info.items():
        channel_id = info.get("id", "")
        if not channel_id:
            continue
        print(f"  Fetching shorts for {handle}...")
        shorts = get_channel_shorts(channel_id, api_key, SHORTS_PER_CHANNEL)
        print(f"    → {len(shorts)} shorts")
        all_shorts.extend(shorts)
        time.sleep(0.3)

    # Add specific short
    print(f"  Adding specific short {SPECIFIC_SHORT_ID}...")
    specific_short = [{
        "video_id": SPECIFIC_SHORT_ID,
        "title": "Specific Short",
        "channel": "Unknown",
        "channel_id": "",
        "url": f"https://www.youtube.com/shorts/{SPECIFIC_SHORT_ID}",
        "published": "",
        "views": "0",
        "likes": "0",
        "comments": "0",
    }]
    all_shorts.extend(specific_short)

    # Get stats for all shorts
    print("  Fetching video stats...")
    video_ids = [s["video_id"] for s in all_shorts]
    stats = get_video_stats(video_ids, api_key)
    for s in all_shorts:
        vid = s["video_id"]
        if vid in stats:
            s["views"] = stats[vid]["views"]
            s["likes"] = stats[vid]["likes"]
            s["comments"] = stats[vid]["comments"]
            s["duration"] = stats[vid]["duration"]

    # Save shorts inventory
    shorts_fields = ["video_id", "title", "channel", "channel_id", "url", "published", "views", "likes", "comments", "duration"]
    write_csv(output_dir / "shorts_inventory.csv", all_shorts, shorts_fields)
    print(f"  Saved shorts_inventory.csv ({len(all_shorts)} shorts)")
    print()

    # ── Step 3: Scrape comments ─────────────────────────────────────────
    print("STEP 3: Scraping comments from shorts...")
    all_rows = []
    for i, short in enumerate(all_shorts, 1):
        vid = short["video_id"]
        print(f"  [{i}/{len(all_shorts)}] {vid} — {short['title'][:50]}...")
        try:
            items, calls = fetch_comments(vid, api_key, MAX_COMMENTS_PER_SHORT)
            rows = []
            for thread in items:
                rows.extend(thread_to_rows(thread, short))
            print(f"    → {len(items)} threads, {len(rows)} comments")
            all_rows.extend(rows)
        except Exception as e:
            print(f"    → ERROR: {e}")
        time.sleep(0.3)

    # Save raw comments
    (output_dir / "raw_comments.json").write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved raw_comments.json ({len(all_rows)} comments)")
    print()

    # ── Step 4: Normalize & extract pain points ─────────────────────────
    print("STEP 4: Normalizing and extracting pain points...")
    normalized = []
    for item in all_rows:
        row = normalize_item(item, "youtube-data-api-v3/commentThreads.list")
        if row:
            for extra in ("video_id", "video_title", "video_channel", "video_views", "video_comments"):
                row[extra] = item.get(extra, "")
            normalized.append(row)

    normalized = dedupe(normalized)
    print(f"  Normalized unique comments: {len(normalized)}")

    extra_fields = ["video_id", "video_title", "video_channel", "video_views", "video_comments"]
    write_csv(output_dir / "normalized_comments.csv", normalized, FIELDS + extra_fields)

    pain_rows = extract_candidates(normalized)
    print(f"  Pain-point candidates: {len(pain_rows)}")

    pain_fields = ["score", "categories", "platform", "comment_text", "engagement_likes",
                   "reply_count", "content_url", "comment_id", "source_actor", "source_run_id"]
    write_csv(output_dir / "painpoint_candidates.csv", pain_rows, pain_fields)
    write_report(output_dir / "painpoint_report.md", normalized, pain_rows)
    print()

    # ── Step 5: Deep channel analysis ──────────────────────────────────
    print("STEP 5: Deep channel analysis...")
    analyses = []
    for handle, info in channels_info.items():
        channel_shorts = [s for s in all_shorts if s.get("channel_id") == info.get("id", "")]
        channel_comments = [c for c in normalized if c.get("channel_or_account") == info.get("snippet", {}).get("title", "")]
        channel_pain = [pp for pp in pain_rows if handle in pp.get("content_url", "") or info.get("snippet", {}).get("title", "") in pp.get("content_url", "")]

        analysis = analyze_channel(info, channel_shorts, channel_comments, channel_pain)
        analyses.append(analysis)
        print(f"  {handle}: {analysis['shorts_analyzed']} shorts, "
              f"{analysis['total_pain_points']} pain points, "
              f"like rate {analysis['like_rate_percent']}%")

    # Save analysis
    (output_dir / "channel_analysis.json").write_text(
        json.dumps(analyses, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print()

    # ── Step 6: Generate content scripts ────────────────────────────────
    print("STEP 6: Generating content scripts...")
    scripts = generate_content_scripts(analyses, pain_rows)
    (output_dir / "content_scripts.md").write_text(scripts, encoding="utf-8")
    print(f"  Saved content_scripts.md")
    print()

    # ── Step 7: Generate SEO tags ──────────────────────────────────────
    print("STEP 7: Generating SEO tags...")
    seo = generate_seo_tags(analyses, pain_rows)
    (output_dir / "seo_tags.json").write_text(
        json.dumps(seo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved seo_tags.json")
    print()

    # ── Summary ─────────────────────────────────────────────────────────
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Channels analyzed: {len(channels_info)}")
    print(f"Shorts fetched: {len(all_shorts)}")
    print(f"Comments scraped: {len(all_rows)}")
    print(f"Normalized comments: {len(normalized)}")
    print(f"Pain-point candidates: {len(pain_rows)}")
    print(f"Output directory: {output_dir}")
    print()
    print("Files generated:")
    for f in sorted(output_dir.iterdir()):
        print(f"  - {f.name}")
    print()
    print("=== DONE ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
