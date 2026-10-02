#!/usr/bin/env python3
"""Competitor Analyzer — lấy từ nikhilbhansali/claude-youtube-skills.

Framework:
- Competitor Discovery (keyword search, content similarity, category search)
- Competitor Ranking (size similarity, engagement rate, overall score)
- Comparative Analysis (metrics comparison)
- Content Gap Analysis
- Output Report Structure

Usage:
    from competitor_analyzer import CompetitorAnalyzer
    analyzer = CompetitorAnalyzer(api_key="YOUR_API_KEY")
    report = analyzer.analyze(target_channel="UC...", competitors=["UC...", "UC..."])
"""
from __future__ import annotations

import json
import logging
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# YouTube Data API v3
YT_API_BASE = "https://www.googleapis.com/youtube/v3"
YT_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")


def load_env_file(path: Path) -> dict[str, str]:
    """Load .env file (utf-8-sig for BOM)."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def get_api_key() -> str:
    """Get YouTube API key from env or .env file."""
    key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY") or YT_API_KEY
    if key:
        return key
    env_path = Path(__file__).resolve().parents[1] / ".env"
    env = load_env_file(env_path)
    return env.get("YOUTUBE_API_KEY") or env.get("YT_API_KEY") or ""


def yt_api_call(endpoint: str, params: dict, api_key: str = "") -> dict:
    """Gọi YouTube Data API v3."""
    key = api_key or get_api_key()
    if not key:
        raise ValueError("Thiếu YOUTUBE_API_KEY")

    params = {k: v for k, v in params.items() if v is not None}
    params["key"] = key
    url = f"{YT_API_BASE}/{endpoint}?{urlencode(params)}"

    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        logger.error(f"API error {e.code}: {body[:200]}")
        return {"error": {"code": e.code, "message": body[:200]}}
    except (URLError, OSError) as e:
        logger.error(f"Network error: {e}")
        return {"error": {"message": str(e)}}


def parse_iso8601_duration(duration: str) -> int:
    """Parse ISO 8601 duration (PT1H30M15S) -> seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


class CompetitorAnalyzer:
    """YouTube Competitor Analyzer."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()

    # ── Discovery ──────────────────────────────────────────────────────────

    def discover_by_keyword(self, query: str, max_results: int = 10) -> list[dict]:
        """Tìm competitor channels bằng keyword search."""
        data = yt_api_call("search", {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": max_results,
        }, self.api_key)

        channels = []
        for item in data.get("items", []):
            channels.append({
                "channel_id": item["snippet"]["channelId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", "")[:200],
            })
        return channels

    def discover_by_content_similarity(self, video_titles: list[str], max_results: int = 10) -> list[dict]:
        """Tìm competitors dựa trên content similarity (từ khóa từ video titles)."""
        # Extract frequent words (>4 chars)
        words = []
        for title in video_titles:
            words.extend(re.findall(r"\b[a-zA-Z]{4,}\b", title.lower()))

        # Count frequency
        from collections import Counter
        word_counts = Counter(words)
        top_words = [w for w, c in word_counts.most_common(10)]

        # Search channels with top words
        channels = []
        for word in top_words[:5]:  # Limit to 5 keywords
            found = self.discover_by_keyword(word, max_results=5)
            channels.extend(found)
            time.sleep(0.5)  # Rate limit

        # Deduplicate
        seen = set()
        unique = []
        for c in channels:
            if c["channel_id"] not in seen:
                seen.add(c["channel_id"])
                unique.append(c)
        return unique[:max_results]

    # ── Channel Details ────────────────────────────────────────────────────

    def get_channel_details(self, channel_ids: list[str]) -> list[dict]:
        """Get channel details (batch, max 50 IDs per call)."""
        if not channel_ids:
            return []

        # Batch in groups of 50
        all_details = []
        for i in range(0, len(channel_ids), 50):
            batch = channel_ids[i:i+50]
            data = yt_api_call("channels", {
                "part": "snippet,statistics,contentDetails,brandingSettings",
                "id": ",".join(batch),
            }, self.api_key)

            for item in data.get("items", []):
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                details = {
                    "channel_id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:200],
                    "published_at": snippet.get("publishedAt", ""),
                    "country": snippet.get("country", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "subscribers": int(stats.get("subscriberCount", 0)),
                    "views": int(stats.get("viewCount", 0)),
                    "video_count": int(stats.get("videoCount", 0)),
                    "keywords": item.get("brandingSettings", {}).get("channel", {}).get("keywords", ""),
                }
                all_details.append(details)
            time.sleep(0.5)

        return all_details

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> list[dict]:
        """Get channel videos (uploads playlist)."""
        # Get uploads playlist ID
        data = yt_api_call("channels", {
            "part": "contentDetails",
            "id": channel_id,
        }, self.api_key)

        if not data.get("items"):
            return []

        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get videos from playlist
        videos = []
        next_page_token = None
        while len(videos) < max_results:
            params = {
                "part": "snippet",
                "playlistId": uploads_id,
                "maxResults": min(50, max_results - len(videos)),
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            data = yt_api_call("playlistItems", params, self.api_key)
            for item in data.get("items", []):
                videos.append({
                    "video_id": item["snippet"]["resourceId"]["videoId"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                })

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
            time.sleep(0.5)

        return videos

    def get_video_details(self, video_ids: list[str]) -> list[dict]:
        """Get video details (batch, max 50 IDs per call)."""
        if not video_ids:
            return []

        all_details = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            data = yt_api_call("videos", {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(batch),
            }, self.api_key)

            for item in data.get("items", []):
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                details = {
                    "video_id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:200],
                    "published_at": snippet.get("publishedAt", ""),
                    "duration": parse_iso8601_duration(item.get("contentDetails", {}).get("duration", "PT0S")),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "tags": snippet.get("tags", []),
                }
                all_details.append(details)
            time.sleep(0.5)

        return all_details

    # ── Ranking ────────────────────────────────────────────────────────────

    def calculate_size_similarity(self, comp_subs: int, target_subs: int) -> float:
        """Size similarity (log scale)."""
        if comp_subs <= 0 or target_subs <= 0:
            return 0.0
        return 1 - abs(math.log10(comp_subs + 1) - math.log10(target_subs + 1)) / 10

    def calculate_engagement_rate(self, views: int, video_count: int) -> float:
        """Engagement per video."""
        return views / max(video_count, 1)

    def calculate_overall_score(self, size_sim: float, relevance: float) -> float:
        """Overall score."""
        return size_sim * 0.3 + relevance * 0.7

    def rank_competitors(self, target: dict, competitors: list[dict]) -> list[dict]:
        """Rank competitors by overall score."""
        target_subs = target.get("subscribers", 0)

        ranked = []
        for comp in competitors:
            size_sim = self.calculate_size_similarity(comp.get("subscribers", 0), target_subs)
            engagement = self.calculate_engagement_rate(comp.get("views", 0), comp.get("video_count", 0))
            # Normalize engagement (log scale)
            engagement_score = min(math.log10(engagement + 1) / 10, 1.0)
            overall = self.calculate_overall_score(size_sim, engagement_score)

            ranked.append({
                **comp,
                "size_similarity": round(size_sim, 3),
                "engagement_rate": round(engagement, 1),
                "overall_score": round(overall, 3),
            })

        return sorted(ranked, key=lambda x: -x["overall_score"])

    # ── Analysis ───────────────────────────────────────────────────────────

    def analyze(self, target_channel_id: str, competitor_ids: list[str] = None) -> dict:
        """Full competitor analysis.

        Args:
            target_channel_id: Channel ID của kênh mình
            competitor_ids: List channel IDs của đối thủ (optional)

        Returns:
            Dict với full analysis report
        """
        # Get target channel details
        target_details = self.get_channel_details([target_channel_id])
        if not target_details:
            raise ValueError(f"Không tìm thấy channel {target_channel_id}")
        target = target_details[0]

        # Discover competitors if not provided
        if not competitor_ids:
            # Get target videos for content similarity
            target_videos = self.get_channel_videos(target_channel_id, max_results=20)
            video_titles = [v["title"] for v in target_videos]
            discovered = self.discover_by_content_similarity(video_titles, max_results=10)
            competitor_ids = [c["channel_id"] for c in discovered]

        # Get competitor details
        competitors = self.get_channel_details(competitor_ids)

        # Rank competitors
        ranked = self.rank_competitors(target, competitors)

        # Comparative analysis
        analysis = self._comparative_analysis(target, ranked)

        # Content gap analysis
        gaps = self._content_gap_analysis(target, ranked)

        return {
            "target": target,
            "competitors": ranked,
            "analysis": analysis,
            "content_gaps": gaps,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _comparative_analysis(self, target: dict, competitors: list[dict]) -> dict:
        """So sánh target vs competitors."""
        if not competitors:
            return {}

        avg_subs = sum(c.get("subscribers", 0) for c in competitors) / len(competitors)
        avg_views = sum(c.get("views", 0) for c in competitors) / len(competitors)
        avg_videos = sum(c.get("video_count", 0) for c in competitors) / len(competitors)
        avg_views_per_video = sum(
            c.get("views", 0) / max(c.get("video_count", 1), 1) for c in competitors
        ) / len(competitors)

        return {
            "avg_competitor_subs": int(avg_subs),
            "avg_competitor_views": int(avg_views),
            "avg_competitor_videos": int(avg_videos),
            "avg_competitor_views_per_video": int(avg_views_per_video),
            "target_subs": target.get("subscribers", 0),
            "target_views": target.get("views", 0),
            "target_videos": target.get("video_count", 0),
            "target_views_per_video": int(target.get("views", 0) / max(target.get("video_count", 1), 1)),
            "subs_ratio": round(target.get("subscribers", 0) / max(avg_subs, 1), 2),
            "views_ratio": round(target.get("views", 0) / max(avg_views, 1), 2),
        }

    def _content_gap_analysis(self, target: dict, competitors: list[dict]) -> dict:
        """Phân tích content gaps."""
        if not competitors:
            return {}

        # Get top competitor videos
        top_competitor = competitors[0]
        top_videos = self.get_channel_videos(top_competitor["channel_id"], max_results=20)
        top_video_ids = [v["video_id"] for v in top_videos]
        top_video_details = self.get_video_details(top_video_ids)

        # Analyze content types
        durations = [v["duration"] for v in top_video_details if v["duration"] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Extract common words from titles
        title_words = []
        for v in top_video_details:
            title_words.extend(re.findall(r"\b[a-zA-Z]{4,}\b", v["title"].lower()))
        from collections import Counter
        common_words = Counter(title_words).most_common(10)

        return {
            "top_competitor": top_competitor["title"],
            "avg_video_duration": int(avg_duration),
            "common_title_words": [w for w, c in common_words],
            "content_types": self._classify_content_types(top_video_details),
        }

    def _classify_content_types(self, videos: list[dict]) -> dict:
        """Phân loại content types."""
        types = {"short": 0, "medium": 0, "long": 0, "livestream": 0}
        for v in videos:
            duration = v.get("duration", 0)
            title = v.get("title", "").lower()
            if "live" in title:
                types["livestream"] += 1
            elif duration <= 60:
                types["short"] += 1
            elif duration <= 600:
                types["medium"] += 1
            else:
                types["long"] += 1
        return types

    # ── Report ─────────────────────────────────────────────────────────────

    def generate_report(self, analysis: dict) -> str:
        """Generate markdown report."""
        target = analysis["target"]
        competitors = analysis["competitors"]
        comp = analysis["analysis"]
        gaps = analysis["content_gaps"]

        lines = [
            "# Competitive Analysis Report",
            f"Generated: {analysis['generated_at']}",
            "",
            "## Executive Summary",
            f"- Target: **{target['title']}** ({target['subscribers']:,} subs)",
            f"- Competitors analyzed: {len(competitors)}",
            f"- Avg competitor subs: {comp.get('avg_competitor_subs', 0):,}",
            f"- Target vs avg: {comp.get('subs_ratio', 0)}x",
            "",
            "## Competitor Table",
            "| Channel | Subs | Videos | Views | Views/Video | Score |",
            "|---------|------|--------|-------|------------|-------|",
        ]

        for c in competitors[:10]:
            lines.append(
                f"| {c['title'][:30]} | {c.get('subscribers', 0):,} | "
                f"{c.get('video_count', 0)} | {c.get('views', 0):,} | "
                f"{c.get('views', 0) // max(c.get('video_count', 1), 1):,} | "
                f"{c.get('overall_score', 0):.3f} |"
            )

        lines += [
            "",
            "## Competitive Positioning",
            f"- Target subs: {comp.get('target_subs', 0):,}",
            f"- Avg competitor subs: {comp.get('avg_competitor_subs', 0):,}",
            f"- Target views/video: {comp.get('target_views_per_video', 0):,}",
            f"- Avg competitor views/video: {comp.get('avg_competitor_views_per_video', 0):,}",
            "",
            "## Content Strategy Comparison",
            f"- Top competitor: {gaps.get('top_competitor', 'N/A')}",
            f"- Avg video duration: {gaps.get('avg_video_duration', 0)}s",
            f"- Common title words: {', '.join(gaps.get('common_title_words', [])[:5])}",
            "",
            "## Opportunities",
            "- Content gaps to fill",
            "- Underserved niches",
            "- Schedule optimization",
            "",
            "## Recommendations",
            "1. Focus on content gaps",
            "2. Optimize upload schedule",
            "3. Improve engagement rate",
        ]

        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = CompetitorAnalyzer()

    # Test với kênh mình
    target_id = "UCBZ7LaffmEPv91sWcfroJdQ"  # @azzammastertradinggold

    print("Analyzing competitors...")
    analysis = analyzer.analyze(target_id)

    print("\n" + "="*60)
    print(analyzer.generate_report(analysis))
