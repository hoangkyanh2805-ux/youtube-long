#!/usr/bin/env python3
"""Comment Filter — lấy từ bellingcat/youtube-comment-scraper.

Features:
- Spam filtering (lọc comment rác)
- User comment tracking (theo dõi user bình luận nhiều video)
- Active author detection (tìm user tích cực)

Usage:
    from comment_filter import CommentFilter
    filter = CommentFilter()
    clean_comments = filter.filter_spam(comments)
    active_authors = filter.find_active_authors(comments)
"""
from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from typing import Literal

logger = logging.getLogger(__name__)


class CommentFilter:
    """Comment filtering và user tracking."""

    def __init__(
        self,
        min_length: int = 5,
        max_emoji_ratio: float = 0.8,
        spam_keywords: list[str] = None,
    ):
        self.min_length = min_length
        self.max_emoji_ratio = max_emoji_ratio
        self.spam_keywords = spam_keywords or [
            "subscribe", "subcribe", "subscrib", "check out my", "my channel",
            "free money", "click here", "link in", "bio", "dm me", "whatsapp",
            "telegram", "signal", "join my", "group chat", "crypto signal",
            "forex signal", "guaranteed profit", "100% win", "risk free",
        ]

    # ── Spam Detection ────────────────────────────────────────────────────

    def is_spam(self, comment: dict) -> bool:
        """Check comment có phải spam không.

        Args:
            comment: {"comment_text": "...", "author_name": "...", ...}

        Returns:
            True nếu là spam
        """
        text = comment.get("comment_text", "").strip()
        author = comment.get("author_name", "").lower()

        # 1. Quá ngắn
        if len(text) < self.min_length:
            return True

        # 2. Chỉ có emoji
        if self._is_only_emoji(text):
            return True

        # 3. Chỉ có số
        if text.isdigit():
            return True

        # 4. Chỉ có link
        if self._is_only_link(text):
            return True

        # 5. Spam keywords
        text_lower = text.lower()
        for keyword in self.spam_keywords:
            if keyword in text_lower:
                return True

        # 6. Lặp lại ký tự (e.g., "aaaaaaa", "!!!!!")
        if self._is_repeated_char(text):
            return True

        # 7. Quá nhiều viết hoa (>80%)
        if self._is_mostly_uppercase(text):
            return True

        # 8. Author name chứa spam keywords
        if any(kw in author for kw in ["signal", "crypto", "forex", "trade", "profit"]):
            return True

        return False

    def _is_only_emoji(self, text: str) -> bool:
        """Check text chỉ có emoji."""
        # Remove emoji và ký tự đặc biệt, xem còn lại gì không
        cleaned = re.sub(r'[^\w\s]', '', text)
        return len(cleaned.strip()) == 0 and len(text) > 0

    def _is_only_link(self, text: str) -> bool:
        """Check text chỉ có link."""
        # Nếu text chứa http/www và không có từ nghĩa
        if "http" in text or "www." in text:
            # Remove link, xem còn lại gì không
            cleaned = re.sub(r'http\S+|www\.\S+', '', text)
            return len(cleaned.strip()) < 5
        return False

    def _is_repeated_char(self, text: str) -> bool:
        """Check text có lặp lại ký tự không."""
        if len(text) < 10:
            return False
        # Đếm ký tự phổ biến nhất
        counter = Counter(text.lower())
        most_common = counter.most_common(1)
        if not most_common:
            return False
        char, count = most_common[0]
        # Nếu 1 ký tự chiếm > 50% độ dài
        return count / len(text) > 0.5

    def _is_mostly_uppercase(self, text: str) -> bool:
        """Check text có quá nhiều viết hoa không."""
        letters = [c for c in text if c.isalpha()]
        if len(letters) < 5:
            return False
        uppercase = [c for c in letters if c.isupper()]
        return len(uppercase) / len(letters) > 0.8

    def filter_spam(self, comments: list[dict]) -> list[dict]:
        """Lọc spam từ list comments.

        Returns:
            List comments không phải spam
        """
        clean = []
        spam_count = 0
        for c in comments:
            if self.is_spam(c):
                spam_count += 1
            else:
                clean.append(c)
        logger.info(f"Filtered {spam_count} spam comments, kept {len(clean)}")
        return clean

    # ── User Tracking ─────────────────────────────────────────────────────

    def track_authors(self, comments: list[dict]) -> dict:
        """Theo dõi user bình luận nhiều video.

        Returns:
            {
                "author_name": {
                    "comment_count": 5,
                    "videos": ["video1", "video2"],
                    "total_likes": 10,
                    "comments": [...]
                }
            }
        """
        authors = defaultdict(lambda: {
            "comment_count": 0,
            "videos": set(),
            "total_likes": 0,
            "comments": [],
        })

        for c in comments:
            author = c.get("author_name", "Unknown")
            authors[author]["comment_count"] += 1
            authors[author]["videos"].add(c.get("video_id", ""))
            authors[author]["total_likes"] += c.get("engagement_likes", 0)
            authors[author]["comments"].append(c)

        # Convert set to list for JSON serialization
        result = {}
        for author, data in authors.items():
            result[author] = {
                "comment_count": data["comment_count"],
                "videos": list(data["videos"]),
                "total_likes": data["total_likes"],
                "comments": data["comments"],
            }
        return result

    def find_active_authors(self, comments: list[dict], min_comments: int = 3) -> list[dict]:
        """Tìm user bình luận tích cực (>= min_comments).

        Returns:
            List of {"author_name": "...", "comment_count": N, "videos": [...]}
        """
        authors = self.track_authors(comments)
        active = []
        for author, data in authors.items():
            if data["comment_count"] >= min_comments:
                active.append({
                    "author_name": author,
                    "comment_count": data["comment_count"],
                    "videos": data["videos"],
                    "total_likes": data["total_likes"],
                })
        return sorted(active, key=lambda x: -x["comment_count"])

    def find_cross_video_authors(self, comments: list[dict], min_videos: int = 2) -> list[dict]:
        """Tìm user bình luận trên nhiều video (cross-video).

        Returns:
            List of {"author_name": "...", "video_count": N, "videos": [...]}
        """
        authors = self.track_authors(comments)
        cross = []
        for author, data in authors.items():
            if len(data["videos"]) >= min_videos:
                cross.append({
                    "author_name": author,
                    "video_count": len(data["videos"]),
                    "videos": data["videos"],
                    "comment_count": data["comment_count"],
                })
        return sorted(cross, key=lambda x: -x["video_count"])

    # ── Statistics ────────────────────────────────────────────────────────

    def get_stats(self, comments: list[dict]) -> dict:
        """Thống kê comments."""
        if not comments:
            return {}

        total = len(comments)
        spam = sum(1 for c in comments if self.is_spam(c))
        clean = total - spam

        # Sentiment distribution (nếu có sentiment field)
        sentiments = Counter()
        for c in comments:
            sentiment = c.get("sentiment", "unknown")
            sentiments[sentiment] += 1

        # Author distribution
        authors = self.track_authors(comments)
        author_counts = [a["comment_count"] for a in authors.values()]

        return {
            "total_comments": total,
            "spam_comments": spam,
            "clean_comments": clean,
            "spam_rate": round(spam / total * 100, 1) if total > 0 else 0,
            "unique_authors": len(authors),
            "avg_comments_per_author": round(sum(author_counts) / len(author_counts), 1) if author_counts else 0,
            "sentiment_distribution": dict(sentiments),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    filter = CommentFilter()

    # Test với dữ liệu thật
    import csv
    from pathlib import Path

    comments = []
    csv_path = Path("outputs/competitor_longform/normalized_comments.csv")
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                comments.append({
                    "comment_id": row.get("comment_id", ""),
                    "comment_text": row.get("comment_text", ""),
                    "author_name": row.get("author_name", ""),
                    "video_id": row.get("video_id", ""),
                    "engagement_likes": int(row.get("engagement_likes", 0)),
                })

    print(f"Loaded {len(comments)} comments")
    print()

    # Test spam filtering
    clean = filter.filter_spam(comments)
    print(f"Clean comments: {len(clean)}")
    print()

    # Test stats
    stats = filter.get_stats(comments)
    print("Stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print()

    # Test active authors
    active = filter.find_active_authors(comments, min_comments=2)
    print(f"Active authors (>=2 comments): {len(active)}")
    for a in active[:5]:
        print(f"  {a['author_name']}: {a['comment_count']} comments, {len(a['videos'])} videos")
