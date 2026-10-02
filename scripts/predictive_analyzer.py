#!/usr/bin/env python3
"""Predictive Analyzer — lấy từ zainmz/Youtube-Channel-Analytics-Dashboard.

Features:
- View forecasting (Prophet hoặc linear regression)
- Tag word cloud (top tags)
- Like-to-view ratio analysis
- Network centrality (đơn giản)

Usage:
    from predictive_analyzer import PredictiveAnalyzer
    analyzer = PredictiveAnalyzer()
    forecast = analyzer.forecast_views(dates, views, periods=30)
    top_tags = analyzer.extract_top_tags(videos, n=20)
"""
from __future__ import annotations

import logging
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Literal

logger = logging.getLogger(__name__)


class PredictiveAnalyzer:
    """Predictive analytics cho YouTube channel."""

    def __init__(self, mode: Literal["simple", "prophet"] = "simple"):
        self.mode = mode

    # ── View Forecasting ───────────────────────────────────────────────────

    def forecast_views(
        self,
        dates: list,
        views: list,
        periods: int = 30,
    ) -> dict:
        """Forecast views cho tương lai.

        Args:
            dates: List datetime objects
            views: List view counts
            periods: Số ngày forecast

        Returns:
            {
                "forecast_dates": [...],
                "forecast_views": [...],
                "trend": "up"|"down"|"stable",
                "growth_rate": 0.05,
            }
        """
        if len(dates) < 3:
            return {
                "forecast_dates": [],
                "forecast_views": [],
                "trend": "stable",
                "growth_rate": 0.0,
            }

        if self.mode == "prophet":
            return self._forecast_prophet(dates, views, periods)
        else:
            return self._forecast_linear(dates, views, periods)

    def _forecast_linear(self, dates: list, views: list, periods: int) -> dict:
        """Linear regression forecasting (simple mode)."""
        # Convert dates to ordinal numbers
        base_date = min(dates)
        x = [(d - base_date).days for d in dates]
        y = views

        n = len(x)
        if n < 2:
            return {"forecast_dates": [], "forecast_views": [], "trend": "stable", "growth_rate": 0.0}

        # Linear regression: y = mx + b
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return {"forecast_dates": [], "forecast_views": [], "trend": "stable", "growth_rate": 0.0}

        m = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - m * sum_x) / n

        # Forecast future dates
        last_date = max(dates)
        forecast_dates = []
        forecast_views = []
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=i)
            forecast_dates.append(future_date)
            forecast_views.append(max(0, int(m * (future_date - base_date).days + b)))

        # Calculate trend
        if len(views) >= 2:
            recent_avg = sum(views[-5:]) / min(5, len(views))
            old_avg = sum(views[:5]) / min(5, len(views))
            growth_rate = (recent_avg - old_avg) / max(old_avg, 1)
        else:
            growth_rate = 0.0

        trend = "up" if growth_rate > 0.05 else "down" if growth_rate < -0.05 else "stable"

        return {
            "forecast_dates": [d.isoformat() for d in forecast_dates],
            "forecast_views": forecast_views,
            "trend": trend,
            "growth_rate": round(growth_rate, 3),
        }

    def _forecast_prophet(self, dates: list, views: list, periods: int) -> dict:
        """Prophet forecasting (nếu đã cài prophet)."""
        try:
            from prophet import Prophet
        except ImportError:
            logger.warning("Prophet not installed, falling back to linear regression")
            return self._forecast_linear(dates, views, periods)

        import pandas as pd

        # Prepare dataframe
        df = pd.DataFrame({"ds": dates, "y": views})

        # Fit model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
            seasonality_mode="additive",
        )
        model.fit(df)

        # Forecast
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        # Extract forecasted period
        forecasted = forecast[forecast["ds"] > df["ds"].max()]

        # Calculate trend
        if len(views) >= 2:
            recent_avg = sum(views[-5:]) / min(5, len(views))
            old_avg = sum(views[:5]) / min(5, len(views))
            growth_rate = (recent_avg - old_avg) / max(old_avg, 1)
        else:
            growth_rate = 0.0

        trend = "up" if growth_rate > 0.05 else "down" if growth_rate < -0.05 else "stable"

        return {
            "forecast_dates": [d.isoformat() for d in forecasted["ds"].tolist()],
            "forecast_views": [int(v) for v in forecasted["yhat"].tolist()],
            "trend": trend,
            "growth_rate": round(growth_rate, 3),
        }

    # ── Tag Analysis ──────────────────────────────────────────────────────

    def extract_top_tags(self, videos: list[dict], n: int = 20) -> list[dict]:
        """Extract top tags từ videos.

        Input: [{"tags": ["tag1", "tag2"], ...}, ...]
        Output: [{"tag": "...", "count": N}, ...]
        """
        all_tags = []
        for v in videos:
            tags = v.get("tags", [])
            if isinstance(tags, str):
                # Tags có thể là string (comma-separated)
                tags = [t.strip() for t in tags.split(",")]
            all_tags.extend(tags)

        counter = Counter(all_tags)
        return [{"tag": tag, "count": count} for tag, count in counter.most_common(n)]

    def extract_title_keywords(self, videos: list[dict], n: int = 20) -> list[dict]:
        """Extract top keywords từ video titles.

        Input: [{"title": "...", ...}, ...]
        Output: [{"keyword": "...", "count": N}, ...]
        """
        stop_words = {
            "the", "and", "for", "with", "from", "this", "that", "your", "you",
            "how", "what", "when", "where", "which", "while", "will", "would",
            "could", "should", "about", "into", "over", "under", "between",
            "through", "during", "before", "after", "above", "below", "then",
            "than", "also", "just", "like", "more", "most", "some", "such",
            "only", "other", "these", "those", "being", "does", "done", "down",
            "each", "even", "ever", "every", "few", "first", "found", "give",
            "good", "great", "hand", "high", "home", "however", "keep", "kind",
            "know", "last", "less", "life", "line", "long", "look", "made",
            "make", "many", "might", "much", "must", "name", "need", "never",
            "next", "night", "note", "nothing", "number", "often", "once",
            "open", "order", "page", "part", "people", "place", "point",
            "power", "press", "price", "product", "public", "quite", "rate",
            "read", "real", "right", "room", "same", "second", "seem", "sense",
            "serve", "several", "show", "side", "since", "small", "social",
            "society", "sort", "sound", "south", "space", "speak", "special",
            "stand", "start", "state", "still", "story", "study", "sure",
            "system", "table", "take", "team", "tell", "term", "test", "them",
            "there", "they", "thing", "think", "this", "those", "though",
            "thought", "three", "time", "today", "together", "tomorrow",
            "tonight", "total", "touch", "toward", "trade", "training",
            "travel", "treat", "true", "truth", "turn", "type", "unit",
            "until", "upon", "value", "very", "view", "visit", "voice", "wait",
            "walk", "want", "watch", "water", "week", "well", "west", "white",
            "whole", "whose", "wide", "wife", "wind", "window", "wish",
            "within", "without", "woman", "word", "work", "world", "worry",
            "worse", "worst", "worth", "would", "write", "wrong", "year",
            "young", "youth", "zone",
        }

        words = []
        for v in videos:
            title = v.get("title", "").lower()
            words.extend(re.findall(r"\b[a-z]{4,}\b", title))

        # Filter stop words
        words = [w for w in words if w not in stop_words]

        counter = Counter(words)
        return [{"keyword": kw, "count": count} for kw, count in counter.most_common(n)]

    # ── Like-to-View Ratio ────────────────────────────────────────────────

    def calculate_like_view_ratio(self, videos: list[dict]) -> list[dict]:
        """Calculate like-to-view ratio cho mỗi video.

        Input: [{"title": "...", "views": N, "likes": N, ...}, ...]
        Output: [{"title": "...", "ratio": 0.05, ...}, ...]
        """
        result = []
        for v in videos:
            views = v.get("views", 0)
            likes = v.get("likes", 0)
            ratio = likes / views if views > 0 else 0
            result.append({
                "title": v.get("title", ""),
                "views": views,
                "likes": likes,
                "ratio": round(ratio, 4),
            })
        return sorted(result, key=lambda x: -x["ratio"])

    def get_avg_like_view_ratio(self, videos: list[dict]) -> float:
        """Average like-to-view ratio."""
        if not videos:
            return 0.0
        total_views = sum(v.get("views", 0) for v in videos)
        total_likes = sum(v.get("likes", 0) for v in videos)
        return round(total_likes / max(total_views, 1), 4)

    # ── Growth Analysis ───────────────────────────────────────────────────

    def analyze_growth(self, videos: list[dict]) -> dict:
        """Analyze channel growth.

        Input: [{"published_at": "...", "views": N, ...}, ...]
        Output: {
            "total_views": N,
            "avg_views_per_video": N,
            "views_trend": "up"|"down"|"stable",
            "best_video": {...},
            "worst_video": {...},
        }
        """
        if not videos:
            return {}

        # Sort by published date
        sorted_videos = sorted(videos, key=lambda x: x.get("published_at", ""))

        total_views = sum(v.get("views", 0) for v in videos)
        avg_views = total_views // len(videos)

        # Find best/worst
        best = max(videos, key=lambda x: x.get("views", 0))
        worst = min(videos, key=lambda x: x.get("views", 0))

        # Trend (first half vs second half)
        mid = len(sorted_videos) // 2
        first_half = sorted_videos[:mid]
        second_half = sorted_videos[mid:]

        first_avg = sum(v.get("views", 0) for v in first_half) / max(len(first_half), 1)
        second_avg = sum(v.get("views", 0) for v in second_half) / max(len(second_half), 1)

        growth_rate = (second_avg - first_avg) / max(first_avg, 1)
        trend = "up" if growth_rate > 0.1 else "down" if growth_rate < -0.1 else "stable"

        return {
            "total_views": total_views,
            "avg_views_per_video": avg_views,
            "views_trend": trend,
            "growth_rate": round(growth_rate, 3),
            "best_video": {
                "title": best.get("title", ""),
                "views": best.get("views", 0),
            },
            "worst_video": {
                "title": worst.get("title", ""),
                "views": worst.get("views", 0),
            },
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = PredictiveAnalyzer(mode="simple")

    # Test với dữ liệu thật
    import csv
    from pathlib import Path

    videos = []
    csv_path = Path("outputs/competitor_longform/longform_inventory.csv")
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                videos.append({
                    "title": row.get("title", ""),
                    "views": int(row.get("views", 0)),
                    "likes": int(row.get("likes", 0)),
                    "published_at": row.get("published", ""),
                    "tags": row.get("tags", ""),
                })

    print(f"Loaded {len(videos)} videos")
    print()

    # Test growth analysis
    growth = analyzer.analyze_growth(videos)
    print("Growth Analysis:")
    for k, v in growth.items():
        print(f"  {k}: {v}")
    print()

    # Test like-to-view ratio
    ratios = analyzer.calculate_like_view_ratio(videos)
    print("Top 5 Like-to-View Ratio:")
    for r in ratios[:5]:
        print(f"  {r['title'][:50]}: {r['ratio']:.4f} ({r['likes']}/{r['views']})")
    print()

    # Test title keywords
    keywords = analyzer.extract_title_keywords(videos, n=10)
    print("Top 10 Title Keywords:")
    for kw in keywords:
        print(f"  {kw['keyword']}: {kw['count']}")
