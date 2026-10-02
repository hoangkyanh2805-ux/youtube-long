#!/usr/bin/env python3
"""Automation Scheduler — lấy từ darkzOGx/youtube-automation-agent.

Features:
- Publish queue management
- Optimal publish time calculation
- Content calendar
- Automation pipeline
- Schedule optimization

Usage:
    from automation_scheduler import AutomationScheduler
    scheduler = AutomationScheduler()
    scheduler.add_to_queue(content)
    scheduler.optimize_schedule()
    scheduler.get_upcoming(days=7)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
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


class AutomationScheduler:
    """Automation Scheduler — quản lý publish queue và content calendar."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        self.publish_queue: list[dict] = []
        self.content_calendar: list[dict] = []

    # ── Publish Queue ─────────────────────────────────────────────────────

    def add_to_queue(
        self,
        content_id: str,
        title: str,
        publish_time: str,
        priority: int = 5,
        metadata: dict = None,
    ) -> dict:
        """Add content vào publish queue.

        Args:
            content_id: ID của content
            title: Tiêu đề
            publish_time: Thời gian publish (ISO format)
            priority: Độ ưu tiên (1-10)
            metadata: Metadata bổ sung

        Returns:
            Schedule entry
        """
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

    # ── Optimal Publish Time ──────────────────────────────────────────────

    def calculate_optimal_times(self, videos: list[dict]) -> dict:
        """Calculate optimal publish times từ video performance.

        Input: [{"published_at": "...", "views": N, ...}, ...]
        Output: {
            "best_days": ["Tuesday", "Wednesday"],
            "best_hours": [14, 15, 16],
            "worst_days": ["Monday", "Friday"],
            "worst_hours": [0, 1, 2, ...],
        }
        """
        if not videos:
            return {
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "best_hours": [14, 15, 16],
                "worst_days": ["Monday", "Friday"],
                "worst_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 22, 23],
            }

        # Analyze views by day of week
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

        # Sort by views
        sorted_days = sorted(day_views.items(), key=lambda x: -x[1])
        sorted_hours = sorted(hour_views.items(), key=lambda x: -x[1])

        best_days = [d for d, _ in sorted_days[:3]]
        best_hours = [h for h, _ in sorted_hours[:3]]
        worst_days = [d for d, _ in sorted_days[-2:]]
        worst_hours = [h for h, _ in sorted_hours[-5:]]

        return {
            "best_days": best_days,
            "best_hours": best_hours,
            "worst_days": worst_days,
            "worst_hours": worst_hours,
        }

    def optimize_schedule(self) -> list[dict]:
        """Optimize publish times trong queue."""
        if not self.publish_queue:
            return []

        # Get optimal times (có thể từ analytics)
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

            # Nếu đã optimal, giữ nguyên
            if current_day in optimal["best_days"] and current_hour in optimal["best_hours"]:
                optimized.append(entry)
                continue

            # Tìm thời gian optimal tiếp theo
            new_time = self._find_next_optimal_time(current_time, optimal)
            if new_time:
                entry["publish_time"] = new_time.isoformat()
                optimized.append(entry)

        return optimized

    def _find_next_optimal_time(self, current_time: datetime, optimal: dict) -> datetime | None:
        """Find next optimal publish time."""
        # Try same day, next optimal hour
        for hour in optimal["best_hours"]:
            if hour > current_time.hour:
                candidate = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                if candidate > current_time:
                    return candidate

        # Try next optimal day
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

    # ── Content Calendar ──────────────────────────────────────────────────

    def generate_calendar(self, days: int = 30) -> list[dict]:
        """Generate content calendar cho N ngày tới."""
        calendar = []
        now = datetime.now(timezone.utc)

        for i in range(days):
            date = now + timedelta(days=i)
            day_name = date.strftime("%A")

            # Determine content type based on day
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

        return calendar

    # ── Automation Pipeline ───────────────────────────────────────────────

    def run_pipeline(self, content_list: list[dict]) -> dict:
        """Run automation pipeline.

        1. Add content to queue
        2. Optimize schedule
        3. Generate calendar
        4. Return summary
        """
        # Add to queue
        for content in content_list:
            self.add_to_queue(
                content_id=content.get("id", ""),
                title=content.get("title", ""),
                publish_time=content.get("publish_time", ""),
                priority=content.get("priority", 5),
                metadata=content.get("metadata", {}),
            )

        # Optimize
        optimized = self.optimize_schedule()

        # Generate calendar
        calendar = self.generate_calendar(days=30)

        return {
            "queue_size": len(self.publish_queue),
            "optimized_count": len(optimized),
            "calendar_days": len(calendar),
            "upcoming_7d": len(self.get_upcoming(days=7)),
            "ready_to_publish": len(self.get_ready_to_publish()),
        }

    # ── Report ────────────────────────────────────────────────────────────

    def generate_report(self) -> dict:
        """Generate automation report."""
        return {
            "queue_status": {
                "total": len(self.publish_queue),
                "scheduled": sum(1 for e in self.publish_queue if e["status"] == "scheduled"),
                "published": sum(1 for e in self.publish_queue if e["status"] == "published"),
                "failed": sum(1 for e in self.publish_queue if e["status"] == "failed"),
            },
            "upcoming_7d": self.get_upcoming(days=7),
            "ready_to_publish": self.get_ready_to_publish(),
            "calendar_next_7d": self.generate_calendar(days=7),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = AutomationScheduler()

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
                    "published_at": row.get("published", ""),
                })

    print(f"Loaded {len(videos)} videos")
    print()

    # Test optimal times
    optimal = scheduler.calculate_optimal_times(videos)
    print("Optimal Publish Times:")
    print(f"  Best days: {optimal['best_days']}")
    print(f"  Best hours: {optimal['best_hours']}")
    print(f"  Worst days: {optimal['worst_days']}")
    print(f"  Worst hours: {optimal['worst_hours']}")
    print()

    # Test calendar
    calendar = scheduler.generate_calendar(days=7)
    print("Content Calendar (7 days):")
    for day in calendar:
        print(f"  {day['date'][:10]} ({day['day']}): {day['content_type']} (priority {day['priority']})")
    print()

    # Test queue
    for i, v in enumerate(videos[:3]):
        scheduler.add_to_queue(
            content_id=f"vid_{i}",
            title=v["title"],
            publish_time=(datetime.now(timezone.utc) + timedelta(days=i+1)).isoformat(),
            priority=8 - i,
        )

    print(f"Queue size: {len(scheduler.publish_queue)}")
    print(f"Upcoming 7d: {len(scheduler.get_upcoming(days=7))}")
    print(f"Ready to publish: {len(scheduler.get_ready_to_publish())}")
