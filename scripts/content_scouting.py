#!/usr/bin/env python3
"""Content Scouting — lấy từ hesamsheikh/awesome-openclaw-usecases.

Pipeline:
1. Search web/X cho trending topics
2. Check against 90-day catalog (YouTube)
3. Semantic similarity check (keyword matching)
4. Pitch nếu novel vào Telegram

Usage:
    from content_scouting import ContentScout
    scout = ContentScout()
    ideas = scout.find_ideas(keywords=["forex", "trading", "xauusd"])
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# YouTube Data API v3
YT_API_BASE = "https://www.googleapis.com/youtube/v3"


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
    key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY")
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


def extract_keywords(text: str, min_length: int = 4) -> list[str]:
    """Extract keywords from text."""
    words = re.findall(r"\b[a-zA-Z]{" + str(min_length) + r",}\b", text.lower())
    # Filter common stop words
    stop_words = {"this", "that", "with", "from", "have", "been", "were", "they", "their", "there", "where", "when", "what", "which", "while", "would", "could", "should", "about", "into", "over", "under", "between", "through", "during", "before", "after", "above", "below", "then", "than", "also", "just", "like", "more", "most", "some", "such", "only", "other", "these", "those", "being", "does", "done", "down", "each", "even", "ever", "every", "few", "first", "found", "give", "good", "great", "hand", "high", "home", "however", "into", "keep", "kind", "know", "last", "less", "life", "like", "line", "long", "look", "made", "make", "many", "might", "more", "most", "much", "must", "name", "need", "never", "next", "next", "night", "note", "nothing", "number", "often", "once", "only", "open", "order", "other", "over", "page", "part", "people", "place", "point", "power", "press", "price", "product", "public", "quite", "rate", "read", "real", "right", "room", "same", "second", "seem", "sense", "serve", "several", "show", "side", "since", "small", "social", "society", "some", "sort", "sound", "south", "space", "speak", "special", "stand", "start", "state", "still", "story", "study", "such", "sure", "system", "table", "take", "team", "tell", "term", "test", "than", "that", "them", "then", "there", "these", "they", "thing", "think", "this", "those", "though", "thought", "three", "through", "time", "today", "together", "tomorrow", "tonight", "total", "touch", "toward", "trade", "training", "travel", "treat", "true", "truth", "turn", "type", "under", "understand", "unit", "until", "upon", "value", "very", "view", "visit", "voice", "wait", "walk", "want", "watch", "water", "week", "well", "west", "what", "when", "where", "which", "while", "white", "whole", "whose", "wide", "wife", "will", "wind", "window", "wish", "with", "within", "without", "woman", "word", "work", "world", "worry", "worse", "worst", "worth", "would", "write", "wrong", "year", "young", "your", "youth", "zone"}
    return [w for w in words if w not in stop_words]


def jaccard_similarity(text1: str, text2: str) -> float:
    """Tính Jaccard similarity giữa 2 texts."""
    words1 = set(extract_keywords(text1))
    words2 = set(extract_keywords(text2))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


class ContentScout:
    """Content Scouting — tìm chủ đề mới từ web/X, đối chiếu catalog."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        self.catalog: list[dict] = []  # 90-day video catalog
        self.past_pitches: list[dict] = []  # past pitches for dedup

    # ── Catalog Management ────────────────────────────────────────────────

    def load_catalog(self, videos: list[dict]) -> None:
        """Load 90-day video catalog.

        Input: [{"video_id": "...", "title": "...", "published_at": "..."}, ...]
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        self.catalog = []
        for v in videos:
            try:
                pub_date = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
                if pub_date >= cutoff:
                    self.catalog.append(v)
            except (KeyError, ValueError):
                continue
        logger.info(f"Loaded {len(self.catalog)} videos from 90-day catalog")

    def load_catalog_from_csv(self, csv_path: Path) -> None:
        """Load catalog from CSV file."""
        import csv
        videos = []
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                videos.append({
                    "video_id": row.get("video_id", ""),
                    "title": row.get("title", ""),
                    "published_at": row.get("published", row.get("published_at", "")),
                })
        self.load_catalog(videos)

    def fetch_catalog_from_youtube(self, channel_id: str, max_results: int = 50) -> None:
        """Fetch 90-day catalog từ YouTube API."""
        # Get uploads playlist
        data = yt_api_call("channels", {
            "part": "contentDetails",
            "id": channel_id,
        }, self.api_key)

        if not data.get("items"):
            return

        uploads_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get videos
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

        self.load_catalog(videos)

    # ── Web Search ────────────────────────────────────────────────────────

    def search_web(self, query: str, max_results: int = 10) -> list[dict]:
        """Search web cho trending topics (dùng web_search tool của Hermes)."""
        # Note: Trong dagu/Hermes, dùng web_search tool
        # Ở đây chỉ là placeholder — cần tích hợp web_search thực tế
        logger.info(f"Search web: {query}")
        return []

    def search_x_twitter(self, query: str, max_results: int = 10) -> list[dict]:
        """Search X/Twitter cho trending topics."""
        # Note: Cần X API hoặc web scraping
        logger.info(f"Search X/Twitter: {query}")
        return []

    def find_ideas_from_results(self, search_results: list[dict], max_ideas: int = 5) -> list[dict]:
        """Tìm ideas từ kết quả search (manual mode).

        Input: [{"title": "...", "url": "...", "snippet": "..."}, ...]
        Output: [{"topic": "...", "sources": [...], "novel": true/false}, ...]
        """
        ideas = []
        for r in search_results:
            topic = r.get("title", "") or r.get("snippet", "")[:100]
            if topic and self.is_novel(topic):
                ideas.append({
                    "topic": topic,
                    "sources": [r.get("url", "")],
                    "novel": True,
                })
            if len(ideas) >= max_ideas:
                break
        return ideas

    # ── Similarity Check ──────────────────────────────────────────────────

    def is_novel(self, topic: str, threshold: float = 0.3) -> bool:
        """Check topic có novel không (so với catalog + past pitches)."""
        # Check against catalog
        for video in self.catalog:
            sim = jaccard_similarity(topic, video.get("title", ""))
            if sim > threshold:
                logger.info(f"Topic '{topic[:50]}' trùng với catalog: {video['title'][:50]} (sim={sim:.2f})")
                return False

        # Check against past pitches
        for pitch in self.past_pitches:
            sim = jaccard_similarity(topic, pitch.get("topic", ""))
            if sim > threshold:
                logger.info(f"Topic '{topic[:50]}' trùng với past pitch (sim={sim:.2f})")
                return False

        return True

    # ── Pitch ─────────────────────────────────────────────────────────────

    def add_pitch(self, topic: str, sources: list[str] = None) -> None:
        """Add pitch vào database."""
        self.past_pitches.append({
            "topic": topic,
            "sources": sources or [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def pitch_to_telegram(self, topic: str, sources: list[str] = None) -> bool:
        """Pitch idea vào Telegram topic."""
        # Note: Cần tích hợp telegram_reporter
        logger.info(f"Pitch to Telegram: {topic}")
        return True

    # ── Main Pipeline ─────────────────────────────────────────────────────

    def find_ideas(self, keywords: list[str], max_ideas: int = 5) -> list[dict]:
        """Tìm chủ đề mới từ keywords.

        Args:
            keywords: List keywords để search (e.g., ["forex", "trading", "xauusd"])
            max_ideas: Số ideas tối đa

        Returns:
            List of {"topic": "...", "sources": [...], "novel": true/false}
        """
        ideas = []

        # Search web/X cho mỗi keyword
        for keyword in keywords:
            # Web search
            web_results = self.search_web(keyword)
            for r in web_results:
                topic = r.get("title", "")
                if topic and self.is_novel(topic):
                    ideas.append({
                        "topic": topic,
                        "sources": [r.get("url", "")],
                        "novel": True,
                    })

            # X/Twitter search
            x_results = self.search_x_twitter(keyword)
            for r in x_results:
                topic = r.get("text", "")[:100]
                if topic and self.is_novel(topic):
                    ideas.append({
                        "topic": topic,
                        "sources": [r.get("url", "")],
                        "novel": True,
                    })

            if len(ideas) >= max_ideas:
                break

        return ideas[:max_ideas]

    def run_pipeline(self, keywords: list[str], max_ideas: int = 5) -> list[dict]:
        """Run full scouting pipeline.

        1. Search web/X
        2. Check catalog
        3. Check past pitches
        4. Return novel ideas
        """
        logger.info(f"Running content scouting pipeline with keywords: {keywords}")

        # Find ideas
        ideas = self.find_ideas(keywords, max_ideas)

        # Add to past pitches
        for idea in ideas:
            self.add_pitch(idea["topic"], idea["sources"])

        logger.info(f"Found {len(ideas)} novel ideas")
        return ideas


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scout = ContentScout()

    # Load catalog từ CSV
    catalog_path = Path("outputs/competitor_longform/longform_inventory.csv")
    if catalog_path.exists():
        scout.load_catalog_from_csv(catalog_path)
    else:
        print(f"Không tìm thấy {catalog_path}")
        print("Dùng catalog rỗng...")

    # Test với keywords
    keywords = ["forex", "trading", "xauusd", "gold", "scalping"]
    print(f"\nSearching for ideas with keywords: {keywords}")
    print(f"Catalog: {len(scout.catalog)} videos")

    ideas = scout.run_pipeline(keywords, max_ideas=5)

    print(f"\nFound {len(ideas)} novel ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"  {i}. {idea['topic'][:80]}")
        print(f"     Sources: {idea['sources']}")
