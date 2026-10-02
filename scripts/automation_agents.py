#!/usr/bin/env python3
"""Automation Agents — tích hợp từ darkzOGx/youtube-automation-agent.

3 Agents:
1. PublishingSchedulingAgent → PublishQueueManager
   - Schedule content, publish queue, optimize publish times
2. ContentStrategyAgent → ContentStrategyAnalyzer
   - Trend analysis, competitor analysis, content calendar
3. AnalyticsOptimizationAgent → PerformanceAnalyzer
   - Performance analysis, insights, recommendations

Usage:
    from automation_agents import PublishQueueManager, ContentStrategyAnalyzer, PerformanceAnalyzer

    # Publishing
    pub = PublishQueueManager()
    pub.add_to_queue(content_id="vid1", title="My Video", publish_time="2026-10-03T14:00:00Z")
    pub.optimize_schedule()

    # Content Strategy
    strategy = ContentStrategyAnalyzer()
    strategy.analyze_trends(videos)
    calendar = strategy.generate_content_calendar(days=30)

    # Performance
    analyzer = PerformanceAnalyzer()
    report = analyzer.analyze_video_performance(video_id="vid1", analytics_data={...})
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict
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


# ═══════════════════════════════════════════════════════════════════════════
# 1. PUBLISHING SCHEDULING AGENT
# ═══════════════════════════════════════════════════════════════════════════

class PublishQueueManager:
    """PublishingSchedulingAgent — quản lý publish queue và schedule content.

    Lấy từ: agents/publishing-scheduling-agent.js
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        self.publish_queue: list[dict] = []

    def add_to_queue(
        self,
        content_id: str,
        title: str,
        publish_time: str,
        priority: int = 5,
        metadata: dict = None,
    ) -> dict:
        """Add content vào publish queue."""
        entry = {
            "content_id": content_id,
            "title": title,
            "publish_time": publish_time,
            "status": "scheduled",
            "priority": priority,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.publish_queue.append(entry)
        self.publish_queue.sort(key=lambda x: x["publish_time"])
        logger.info(f"Added to queue: {title} at {publish_time}")
        return entry

    def remove_from_queue(self, content_id: str) -> bool:
        """Remove content khỏi publish queue."""
        for i, entry in enumerate(self.publish_queue):
            if entry["content_id"] == content_id:
                self.publish_queue.pop(i)
                logger.info(f"Removed from queue: {content_id}")
                return True
        return False

    def get_upcoming(self, days: int = 7) -> list[dict]:
        """Get upcoming scheduled content."""
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=days)
        return [
            e for e in self.publish_queue
            if e["status"] == "scheduled"
            and now <= datetime.fromisoformat(e["publish_time"].replace("Z", "+00:00")) <= end_date
        ]

    def get_ready_to_publish(self) -> list[dict]:
        """Get content ready to publish (publish_time <= now)."""
        now = datetime.now(timezone.utc)
        return [
            e for e in self.publish_queue
            if e["status"] == "scheduled"
            and datetime.fromisoformat(e["publish_time"].replace("Z", "+00:00")) <= now
        ]

    def calculate_optimal_times(self, videos: list[dict]) -> dict:
        """Calculate optimal publish times từ video performance."""
        if not videos:
            return {
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "best_hours": [14, 15, 16],
                "worst_days": ["Monday", "Friday"],
                "worst_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 22, 23],
            }

        day_views = {}
        hour_views = {}
        for v in videos:
            try:
                pub_date = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
                day = pub_date.strftime("%A")
                hour = pub_date.hour
                views = v.get("views", 0)

                day_views[day] = day_views.get(day, 0) + views
                hour_views[hour] = hour_views.get(hour, 0) + views
            except (KeyError, ValueError):
                continue

        sorted_days = sorted(day_views.items(), key=lambda x: -x[1])
        sorted_hours = sorted(hour_views.items(), key=lambda x: -x[1])

        return {
            "best_days": [d for d, _ in sorted_days[:3]],
            "best_hours": [h for h, _ in sorted_hours[:3]],
            "worst_days": [d for d, _ in sorted_days[-2:]],
            "worst_hours": [h for h, _ in sorted_hours[-5:]],
        }

    def optimize_schedule(self) -> list[dict]:
        """Optimize publish times trong queue."""
        if not self.publish_queue:
            return []

        optimal = {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_hours": [14, 15, 16],
        }

        optimized = []
        for entry in self.publish_queue:
            if entry["status"] != "scheduled":
                continue

            current_time = datetime.fromisoformat(entry["publish_time"].replace("Z", "+00:00"))
            current_day = current_time.strftime("%A")
            current_hour = current_time.hour

            if current_day in optimal["best_days"] and current_hour in optimal["best_hours"]:
                optimized.append(entry)
                continue

            new_time = self._find_next_optimal_time(current_time, optimal)
            if new_time:
                entry["publish_time"] = new_time.isoformat()
                optimized.append(entry)

        return optimized

    def _find_next_optimal_time(self, current_time: datetime, optimal: dict) -> datetime | None:
        """Find next optimal publish time."""
        for hour in optimal["best_hours"]:
            if hour > current_time.hour:
                candidate = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                if candidate > current_time:
                    return candidate

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day_idx = days.index(current_time.strftime("%A"))

        for i in range(1, 8):
            next_day_idx = (current_day_idx + i) % 7
            next_day = days[next_day_idx]
            if next_day in optimal["best_days"]:
                candidate = current_time + timedelta(days=i)
                candidate = candidate.replace(
                    hour=optimal["best_hours"][0],
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                return candidate

        return None

    def generate_report(self) -> dict:
        """Generate publishing report."""
        return {
            "queue_status": {
                "total": len(self.publish_queue),
                "scheduled": sum(1 for e in self.publish_queue if e["status"] == "scheduled"),
                "published": sum(1 for e in self.publish_queue if e["status"] == "published"),
                "failed": sum(1 for e in self.publish_queue if e["status"] == "failed"),
            },
            "upcoming_7d": self.get_upcoming(days=7),
            "ready_to_publish": self.get_ready_to_publish(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# 2. CONTENT STRATEGY AGENT
# ═══════════════════════════════════════════════════════════════════════════

class ContentStrategyAnalyzer:
    """ContentStrategyAgent — trend analysis, competitor analysis, content calendar.

    Lấy từ: agents/content-strategy-agent.js
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        self.trending_topics: list[dict] = []
        self.competitor_data: list[dict] = []
        self.content_calendar: list[dict] = []

    def analyze_trends(self, videos: list[dict]) -> list[dict]:
        """Analyze trends từ video titles và tags."""
        topics = {}
        for v in videos:
            title = v.get("title", "").lower()
            views = v.get("views", 0)

            keywords = self._extract_keywords(title)
            for kw in keywords:
                if kw not in topics:
                    topics[kw] = {"score": 0, "sources": [], "evidence": []}
                topics[kw]["score"] += views / 1000000
                topics[kw]["sources"].append("trending")
                topics[kw]["evidence"].append({
                    "url": v.get("url", ""),
                    "title": v.get("title", ""),
                    "views": views,
                })

        # Sort by score
        sorted_topics = sorted(topics.items(), key=lambda x: -x[1]["score"])
        self.trending_topics = [
            {"topic": topic, **data}
            for topic, data in sorted_topics[:50]
        ]
        return self.trending_topics

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords từ text."""
        stop_words = {
            "the", "is", "at", "which", "on", "and", "a", "an", "as", "are",
            "was", "were", "been", "be", "have", "has", "had", "do", "does",
            "did", "will", "would", "could", "should", "may", "might", "must",
            "can", "i", "you", "he", "she", "it", "we", "they", "what",
            "which", "who", "when", "where", "why", "how", "all", "each",
            "every", "both", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "now",
        }
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        return [w for w in words if len(w) > 3 and w not in stop_words]

    def analyze_competitors(self, competitor_videos: dict[str, list[dict]]) -> list[dict]:
        """Analyze competitor channels.

        Input: {"channel_id": [{"title": "...", "views": N, ...}, ...], ...}
        """
        self.competitor_data = []
        for channel_id, videos in competitor_videos.items():
            if not videos:
                continue

            total_views = sum(v.get("views", 0) for v in videos)
            avg_views = total_views // len(videos)

            # Extract top topics
            topics = {}
            for v in videos:
                title = v.get("title", "").lower()
                views = v.get("views", 0)
                keywords = self._extract_keywords(title)
                for kw in keywords:
                    if kw not in topics:
                        topics[kw] = {"count": 0, "views": 0, "evidence": []}
                    topics[kw]["count"] += 1
                    topics[kw]["views"] += views
                    topics[kw]["evidence"].append({
                        "url": v.get("url", ""),
                        "title": v.get("title", ""),
                    })

            top_topics = sorted(topics.items(), key=lambda x: -x[1]["views"])[:10]

            self.competitor_data.append({
                "channel_id": channel_id,
                "top_topics": [{"topic": t, **data} for t, data in top_topics],
                "average_views": avg_views,
                "upload_frequency": len(videos),
            })

        return self.competitor_data

    def generate_content_calendar(self, days: int = 30) -> list[dict]:
        """Generate content calendar cho N ngày tới."""
        calendar = []
        now = datetime.now(timezone.utc)

        for i in range(days):
            date = now + timedelta(days=i)
            day_name = date.strftime("%A")

            if day_name in ["Tuesday", "Wednesday", "Thursday"]:
                content_type = "long_form"
                priority = 8
            elif day_name in ["Saturday", "Sunday"]:
                content_type = "short"
                priority = 5
            else:
                content_type = "community"
                priority = 3

            calendar.append({
                "date": date.isoformat(),
                "day": day_name,
                "content_type": content_type,
                "priority": priority,
                "status": "planned",
            })

        self.content_calendar = calendar
        return calendar

    def select_optimal_topic(self) -> dict | None:
        """Select optimal topic từ trending topics."""
        if not self.trending_topics:
            return None

        # Filter readable topics
        readable = [
            t for t in self.trending_topics
            if " " in t["topic"].strip() and len(t["topic"].strip()) >= 8
        ]
        if readable:
            return readable[0]

        # Fallback to evergreen topics
        evergreen = [
            "Time Management Strategies That Actually Work",
            "Beginner Mistakes to Avoid When Learning a New Skill",
            "How to Start a Side Project With Zero Budget",
            "Simple Habits That Improve Focus and Productivity",
        ]
        return {"topic": evergreen[0], "score": 1}

    def predict_views(self, topic: str) -> int:
        """Predict views cho topic."""
        topic_data = next(
            (t for t in self.trending_topics if t["topic"] == topic),
            None
        )
        base_views = topic_data["score"] * 10000 if topic_data else 5000
        variance = base_views * 0.3
        import random
        return int(base_views + (random.random() * variance * 2) - variance)

    def calculate_best_publish_time(self) -> str:
        """Calculate best publish time."""
        best_times = [
            {"day": "Tuesday", "hour": 14},
            {"day": "Wednesday", "hour": 14},
            {"day": "Thursday", "hour": 14},
            {"day": "Friday", "hour": 15},
            {"day": "Saturday", "hour": 10},
            {"day": "Sunday", "hour": 10},
        ]
        import random
        selected = random.choice(best_times)
        next_date = self._get_next_weekday(selected["day"])
        next_date = next_date.replace(hour=selected["hour"], minute=0, second=0, microsecond=0)
        return next_date.isoformat()

    def _get_next_weekday(self, day_name: str) -> datetime:
        """Get next occurrence of a weekday."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        target_day = days.index(day_name)
        today = datetime.now(timezone.utc)
        current_day = today.weekday()
        days_until_target = (target_day - current_day + 7) % 7 or 7
        return today + timedelta(days=days_until_target)


# ═══════════════════════════════════════════════════════════════════════════
# 3. ANALYTICS OPTIMIZATION AGENT
# ═══════════════════════════════════════════════════════════════════════════

class PerformanceAnalyzer:
    """AnalyticsOptimizationAgent — performance analysis, insights, recommendations.

    Lấy từ: agents/analytics-optimization-agent.js
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        self.performance_data: dict[str, dict] = {}

    def analyze_video_performance(
        self,
        video_id: str,
        video_details: dict,
        analytics_data: dict,
    ) -> dict:
        """Analyze video performance.

        Args:
            video_id: Video ID
            video_details: {"title": "...", "views": N, "likes": N, ...}
            analytics_data: {"watch_time": N, "avg_view_duration": N, ...}

        Returns:
            Performance report với score, grade, insights, recommendations
        """
        views = video_details.get("views", 0)
        likes = video_details.get("likes", 0)
        comments = video_details.get("comments", 0)
        watch_time = analytics_data.get("watch_time", 0)
        avg_view_duration = analytics_data.get("avg_view_duration", 0)

        # Calculate engagement metrics
        interactions = likes + comments
        engagement_rate = (interactions / views * 100) if views > 0 else 0
        like_ratio = (likes / interactions * 100) if interactions > 0 else 0
        comments_per_view = (comments / views * 100) if views > 0 else 0

        # Calculate performance score
        score = self._calculate_performance_score(
            views, watch_time, engagement_rate, avg_view_duration
        )

        # Generate insights
        insights = self._generate_insights(
            views, watch_time, engagement_rate, avg_view_duration
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            views, watch_time, engagement_rate, avg_view_duration
        )

        report = {
            "video_id": video_id,
            "video_details": video_details,
            "analytics": analytics_data,
            "engagement": {
                "engagement_rate": round(engagement_rate, 2),
                "like_ratio": round(like_ratio, 2),
                "comments_per_view": round(comments_per_view, 4),
                "engagement_quality": self._assess_engagement_quality(engagement_rate),
            },
            "performance": score,
            "insights": insights,
            "recommendations": recommendations,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

        self.performance_data[video_id] = report
        return report

    def _calculate_performance_score(
        self,
        views: int,
        watch_time: int,
        engagement_rate: float,
        avg_view_duration: int,
    ) -> dict:
        """Calculate performance score (0-100)."""
        # Views score (30 points max)
        views_score = min(30, (views / 10000) * 30)

        # Watch time score (25 points max)
        watch_time_score = min(25, (watch_time / 1000) * 25)

        # Engagement score (25 points max)
        engagement_score = min(25, engagement_rate * 5)

        # Duration score (20 points max)
        duration_score = min(20, (avg_view_duration / 300) * 20)

        total = views_score + watch_time_score + engagement_score + duration_score
        final_score = int(total)

        return {
            "score": final_score,
            "breakdown": {
                "views": int(views_score),
                "watch_time": int(watch_time_score),
                "engagement": int(engagement_score),
                "duration": int(duration_score),
            },
            "grade": self._get_performance_grade(final_score),
        }

    def _get_performance_grade(self, score: int) -> str:
        """Get performance grade."""
        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        if score >= 50:
            return "D"
        return "F"

    def _assess_engagement_quality(self, rate: float) -> str:
        """Assess engagement quality."""
        if rate > 8:
            return "excellent"
        if rate > 5:
            return "good"
        if rate > 2:
            return "average"
        return "poor"

    def _generate_insights(
        self,
        views: int,
        watch_time: int,
        engagement_rate: float,
        avg_view_duration: int,
    ) -> list[dict]:
        """Generate insights từ analytics."""
        insights = []

        # Views insights
        if views > 10000:
            insights.append({
                "type": "success",
                "category": "views",
                "message": "Video is performing above average in terms of views",
                "impact": "high",
            })
        elif views < 1000:
            insights.append({
                "type": "warning",
                "category": "views",
                "message": "Video views are below expected threshold",
                "impact": "high",
                "recommendation": "Consider promoting the video or optimizing SEO",
            })

        # Watch time insights
        if watch_time > 5000:
            insights.append({
                "type": "success",
                "category": "watch_time",
                "message": "Excellent watch time",
                "impact": "medium",
            })
        elif watch_time < 500:
            insights.append({
                "type": "warning",
                "category": "watch_time",
                "message": "Low watch time - viewers are dropping off early",
                "impact": "high",
                "recommendation": "Review content structure and pacing",
            })

        # Engagement insights
        if engagement_rate > 5:
            insights.append({
                "type": "success",
                "category": "engagement",
                "message": "High audience engagement",
                "impact": "medium",
            })
        elif engagement_rate < 1:
            insights.append({
                "type": "warning",
                "category": "engagement",
                "message": "Low audience engagement",
                "impact": "medium",
                "recommendation": "Encourage more interaction in future videos",
            })

        return insights

    def _generate_recommendations(
        self,
        views: int,
        watch_time: int,
        engagement_rate: float,
        avg_view_duration: int,
    ) -> list[str]:
        """Generate recommendations từ analytics."""
        recommendations = []

        if views < 1000:
            recommendations.append("Optimize title and thumbnail for better CTR")
            recommendations.append("Promote video on social media")

        if watch_time < 500:
            recommendations.append("Improve content pacing and structure")
            recommendations.append("Add hooks in first 30 seconds")

        if engagement_rate < 1:
            recommendations.append("Add call-to-action for comments")
            recommendations.append("Respond to comments to build community")

        if avg_view_duration < 60:
            recommendations.append("Increase video length for better retention")
            recommendations.append("Add more value to keep viewers watching")

        return recommendations

    def get_channel_insights(self) -> dict:
        """Get channel-level insights."""
        if not self.performance_data:
            return {}

        reports = list(self.performance_data.values())
        avg_score = sum(r["performance"]["score"] for r in reports) / len(reports)

        return {
            "total_videos_analyzed": len(reports),
            "average_performance_score": int(avg_score),
            "top_performers": sorted(
                reports,
                key=lambda x: -x["performance"]["score"]
            )[:5],
            "common_issues": self._find_common_issues(reports),
        }

    def _find_common_issues(self, reports: list[dict]) -> list[str]:
        """Find common issues across videos."""
        issues = []
        low_retention = sum(
            1 for r in reports
            if r["analytics"].get("watch_time", 0) < 500
        )
        if low_retention > len(reports) * 0.5:
            issues.append("Multiple videos showing poor retention - review content quality")

        low_engagement = sum(
            1 for r in reports
            if r["engagement"]["engagement_rate"] < 1
        )
        if low_engagement > len(reports) * 0.5:
            issues.append("Multiple videos showing low engagement - improve CTAs")

        return issues


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("AUTOMATION AGENTS — Test")
    print("=" * 60)

    # Test PublishQueueManager
    print("\n1. PublishQueueManager")
    pub = PublishQueueManager()
    pub.add_to_queue("vid1", "Test Video 1", (datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
    pub.add_to_queue("vid2", "Test Video 2", (datetime.now(timezone.utc) + timedelta(days=2)).isoformat())
    print(f"   Queue size: {len(pub.publish_queue)}")
    print(f"   Upcoming 7d: {len(pub.get_upcoming(days=7))}")

    # Test ContentStrategyAnalyzer
    print("\n2. ContentStrategyAnalyzer")
    strategy = ContentStrategyAnalyzer()
    test_videos = [
        {"title": "How to Trade Forex for Beginners", "views": 5000, "url": "https://youtube.com/watch?v=1"},
        {"title": "Best Trading Strategy 2026", "views": 10000, "url": "https://youtube.com/watch?v=2"},
        {"title": "Forex Trading Tips and Tricks", "views": 3000, "url": "https://youtube.com/watch?v=3"},
    ]
    trends = strategy.analyze_trends(test_videos)
    print(f"   Trending topics: {len(trends)}")
    calendar = strategy.generate_content_calendar(days=7)
    print(f"   Calendar days: {len(calendar)}")

    # Test PerformanceAnalyzer
    print("\n3. PerformanceAnalyzer")
    analyzer = PerformanceAnalyzer()
    report = analyzer.analyze_video_performance(
        video_id="vid1",
        video_details={"title": "Test Video", "views": 5000, "likes": 200, "comments": 50},
        analytics_data={"watch_time": 10000, "avg_view_duration": 120},
    )
    print(f"   Performance score: {report['performance']['score']}/100")
    print(f"   Grade: {report['performance']['grade']}")
    print(f"   Insights: {len(report['insights'])}")
    print(f"   Recommendations: {len(report['recommendations'])}")

    print("\n" + "=" * 60)
    print("All agents loaded successfully!")
