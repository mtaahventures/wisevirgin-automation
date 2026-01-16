"""
Content Balancer - Tracks positive/negative video balance (40-60% each)

Ensures channel doesn't become one-dimensional. Highly reusable for any content strategy.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import sqlite3
from datetime import datetime, timedelta
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger("content_balancer", get_daily_log_file())

class ContentBalancer:
    def __init__(self, db_path=None):
        """
        Initialize content balancer with SQLite database

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "../../data/content_balance.db"
            )

        self.db_path = os.path.abspath(db_path)

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_videos (
                    video_id TEXT PRIMARY KEY,
                    event TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    score INTEGER,
                    publish_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_type
                ON content_videos(content_type)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_publish_date
                ON content_videos(publish_date)
            """)

            conn.commit()
            conn.close()

            logger.info(f"Content balance database initialized: {self.db_path}")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def record_video(self, video_id, event, emotion, content_type, score, publish_date=None):
        """
        Record a new video in the balance tracker

        Args:
            video_id: YouTube video ID
            event: Event name
            emotion: Emotion target
            content_type: "positive" or "negative"
            score: Video opportunity score
            publish_date: Publication date (defaults to now)

        Returns:
            bool: Success status
        """
        try:
            if content_type not in ["positive", "negative"]:
                raise ValueError(f"Invalid content_type: {content_type}. Must be 'positive' or 'negative'")

            if publish_date is None:
                publish_date = datetime.now().isoformat()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO content_videos
                (video_id, event, emotion, content_type, score, publish_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (video_id, event, emotion, content_type, score, publish_date))

            conn.commit()
            conn.close()

            logger.info(f"Recorded {content_type} video: {event} + {emotion} (score: {score})")

            return True

        except Exception as e:
            logger.error(f"Record video error: {e}")
            return False

    def get_balance_status(self, days=30):
        """
        Get current positive/negative content balance

        Args:
            days: Number of days to analyze (default 30)

        Returns:
            dict: Balance statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculate date threshold
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Get counts by content type
            cursor.execute("""
                SELECT content_type, COUNT(*) as count
                FROM content_videos
                WHERE publish_date >= ?
                GROUP BY content_type
            """, (threshold_date,))

            results = cursor.fetchall()
            conn.close()

            positive_count = 0
            negative_count = 0

            for content_type, count in results:
                if content_type == "positive":
                    positive_count = count
                elif content_type == "negative":
                    negative_count = count

            total_count = positive_count + negative_count

            if total_count == 0:
                positive_percent = 0
                negative_percent = 0
            else:
                positive_percent = (positive_count / total_count) * 100
                negative_percent = (negative_count / total_count) * 100

            balance_status = {
                "period_days": days,
                "total_videos": total_count,
                "positive": {
                    "count": positive_count,
                    "percent": positive_percent,
                    "in_range": 40 <= positive_percent <= 60
                },
                "negative": {
                    "count": negative_count,
                    "percent": negative_percent,
                    "in_range": 40 <= negative_percent <= 60
                },
                "is_balanced": (40 <= positive_percent <= 60) and (40 <= negative_percent <= 60),
                "timestamp": datetime.now().isoformat()
            }

            logger.info(
                f"Balance status: {positive_percent:.1f}% positive, "
                f"{negative_percent:.1f}% negative (last {days} days)"
            )

            return balance_status

        except Exception as e:
            logger.error(f"Get balance status error: {e}")
            return {
                "period_days": days,
                "total_videos": 0,
                "positive": {"count": 0, "percent": 0, "in_range": False},
                "negative": {"count": 0, "percent": 0, "in_range": False},
                "is_balanced": True,  # No videos = balanced
                "timestamp": datetime.now().isoformat()
            }

    def suggest_next_content_type(self, days=30):
        """
        Suggest next content type to maintain 40-60% balance

        Args:
            days: Number of days to analyze

        Returns:
            str: "positive" or "negative" or "either"
        """
        try:
            balance = self.get_balance_status(days)

            positive_percent = balance["positive"]["percent"]
            negative_percent = balance["negative"]["percent"]

            # If no videos yet, either is fine
            if balance["total_videos"] == 0:
                return "either"

            # If positive is below 40%, need more positive
            if positive_percent < 40:
                logger.info("Suggesting POSITIVE content (rebalancing)")
                return "positive"

            # If positive is above 60%, need more negative
            if positive_percent > 60:
                logger.info("Suggesting NEGATIVE content (rebalancing)")
                return "negative"

            # If negative is below 40%, need more negative
            if negative_percent < 40:
                logger.info("Suggesting NEGATIVE content (rebalancing)")
                return "negative"

            # If negative is above 60%, need more positive
            if negative_percent > 60:
                logger.info("Suggesting POSITIVE content (rebalancing)")
                return "positive"

            # If balanced, either is fine
            logger.info("Content balanced - either type acceptable")
            return "either"

        except Exception as e:
            logger.error(f"Suggest content type error: {e}")
            return "either"

    def get_recent_videos(self, days=30, limit=50):
        """
        Get recent videos with content type

        Args:
            days: Number of days to retrieve
            limit: Maximum number of videos to return

        Returns:
            list: List of video dicts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute("""
                SELECT video_id, event, emotion, content_type, score, publish_date
                FROM content_videos
                WHERE publish_date >= ?
                ORDER BY publish_date DESC
                LIMIT ?
            """, (threshold_date, limit))

            rows = cursor.fetchall()
            conn.close()

            videos = []
            for row in rows:
                videos.append({
                    "video_id": row[0],
                    "event": row[1],
                    "emotion": row[2],
                    "content_type": row[3],
                    "score": row[4],
                    "publish_date": row[5]
                })

            logger.info(f"Retrieved {len(videos)} recent videos")

            return videos

        except Exception as e:
            logger.error(f"Get recent videos error: {e}")
            return []

if __name__ == "__main__":
    # Test the content balancer
    balancer = ContentBalancer()

    # Simulate recording some videos
    balancer.record_video("test1", "AI Joblessness", "Anxiety", "negative", 93)
    balancer.record_video("test2", "Wedding Day", "Joy", "positive", 85)
    balancer.record_video("test3", "Market Crash", "Fear", "negative", 88)

    # Check balance
    balance = balancer.get_balance_status()

    import json
    print("Balance Status:")
    print(json.dumps(balance, indent=2))

    # Get suggestion
    suggestion = balancer.suggest_next_content_type()
    print(f"\nNext content type suggestion: {suggestion}")

    # Get recent videos
    recent = balancer.get_recent_videos(days=7)
    print(f"\nRecent videos: {len(recent)}")
