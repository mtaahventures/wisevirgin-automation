"""
Balanced Scorer - 7-metric data-driven scoring system for video opportunities (0-100 points)

Highly modular and reusable for any event-driven content strategy.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.logging_utils import setup_logger, get_daily_log_file
from googleapiclient.discovery import build
import os
from datetime import datetime

logger = setup_logger("balanced_scorer", get_daily_log_file())

class BalancedScorer:
    def __init__(self, youtube_api_key=None):
        """
        Initialize scorer with configurable thresholds

        Makes the scorer reusable across different content strategies
        """
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY", "")

        # Configurable thresholds for modularity and reuse
        self.search_volume_thresholds = {
            150000: 30,
            100000: 25,
            50000: 20,
            10000: 10,
            1000: 5,
            0: 0
        }

        self.trend_velocity_thresholds = {
            1500: 20,
            500: 15,
            100: 10,
            0: 5,
            -100: 0
        }

        self.competition_thresholds = {
            10: 15,
            50: 12,
            200: 8,
            1000: 4,
            float("inf"): 0
        }

        self.cpm_category_values = {
            "finance": 10,
            "business": 9,
            "technology": 8,
            "health": 8,
            "education": 7,
            "lifestyle": 6,
            "spirituality": 6,
            "entertainment": 5,
            "default": 5
        }

    def score_search_volume(self, volume):
        """
        Score search volume (0-30 points)

        Args:
            volume: Estimated monthly search volume

        Returns:
            int: Score 0-30 points
        """
        for threshold, score in sorted(self.search_volume_thresholds.items(), reverse=True):
            if volume >= threshold:
                return score
        return 0

    def score_trend_velocity(self, velocity_percent):
        """
        Score trend velocity (0-20 points)

        Args:
            velocity_percent: Percentage change in search interest

        Returns:
            int: Score 0-20 points
        """
        for threshold, score in sorted(self.trend_velocity_thresholds.items(), reverse=True):
            if velocity_percent >= threshold:
                return score
        return 0

    def score_competition(self, num_videos):
        """
        Score competition level (0-15 points) - Lower competition = higher score

        Args:
            num_videos: Number of existing videos on the topic

        Returns:
            int: Score 0-15 points
        """
        for threshold, score in sorted(self.competition_thresholds.items()):
            if num_videos < threshold:
                return score
        return 0

    def score_cpm_potential(self, category="default"):
        """
        Score CPM potential based on content category (0-10 points)

        Args:
            category: Content category (finance, health, spirituality, etc.)

        Returns:
            int: Score 0-10 points
        """
        return self.cpm_category_values.get(category.lower(), self.cpm_category_values["default"])

    def score_seasonality(self, is_evergreen=True, is_seasonal=False, is_one_time=False):
        """
        Score content seasonality (0-10 points)

        Args:
            is_evergreen: Content relevant year-round
            is_seasonal: Content relevant during specific seasons
            is_one_time: One-time event

        Returns:
            int: Score 0-10 points
        """
        if is_evergreen:
            return 10
        elif is_seasonal:
            return 5
        elif is_one_time:
            return 2
        return 0

    def score_engagement_signal(self, engagement_count):
        """
        Score social engagement signals (0-10 points)

        Args:
            engagement_count: Total mentions/shares/comments across platforms

        Returns:
            int: Score 0-10 points
        """
        engagement_thresholds = {
            50000: 10,
            25000: 8,
            10000: 6,
            5000: 4,
            1000: 2,
            0: 0
        }

        for threshold, score in sorted(engagement_thresholds.items(), reverse=True):
            if engagement_count >= threshold:
                return score
        return 0

    def score_freshness(self, days_since_event):
        """
        Score content freshness (0-5 points)

        Args:
            days_since_event: Days since event/trend started

        Returns:
            int: Score 0-5 points
        """
        if days_since_event < 1:
            return 5  # Breaking news
        elif days_since_event < 7:
            return 3  # Less than a week
        elif days_since_event < 30:
            return 1  # Less than a month
        return 0  # Older than a month

    def get_youtube_competition(self, event, emotion):
        """
        Check YouTube competition for specific event + emotion combination

        Args:
            event: Event keyword
            emotion: Emotion keyword

        Returns:
            int: Number of competing videos
        """
        try:
            if not self.youtube_api_key:
                logger.warning("No YouTube API key - returning estimated competition")
                # Return estimated competition based on specificity
                if len(event.split()) > 3 and len(emotion.split()) > 1:
                    return 5  # Very specific = low competition
                elif len(event.split()) > 2:
                    return 50  # Moderately specific
                else:
                    return 200  # Generic = high competition

            youtube = build("youtube", "v3", developerKey=self.youtube_api_key)

            search_query = f"bible verses for {emotion} {event}"

            search_response = youtube.search().list(
                q=search_query,
                part="snippet",
                type="video",
                maxResults=50
            ).execute()

            num_results = search_response.get("pageInfo", {}).get("totalResults", 0)

            logger.info(f"Competition check: {search_query} = {num_results} videos")

            return min(num_results, 1000)  # Cap at 1000 for scoring

        except Exception as e:
            logger.error(f"YouTube competition check error: {e}")
            return 50  # Default moderate competition

    def score_video_opportunity(self, event_data, emotion, category="spirituality"):
        """
        Calculate total score for a video opportunity (0-100 points)

        Args:
            event_data: Dict with event tracking data
            emotion: Target emotion for the video
            category: Content category for CPM estimation

        Returns:
            dict: Detailed scoring breakdown
        """
        # Extract event metrics
        search_volume = event_data.get("search_volume", 0)
        trend_velocity = event_data.get("trend_velocity", 0)
        freshness_days = event_data.get("freshness_days", 7)
        engagement = event_data.get("engagement", 0)

        # Calculate individual scores
        search_score = self.score_search_volume(search_volume)
        velocity_score = self.score_trend_velocity(trend_velocity)

        # Get YouTube competition
        competition_count = self.get_youtube_competition(
            event_data.get("event", ""),
            emotion
        )
        competition_score = self.score_competition(competition_count)

        cpm_score = self.score_cpm_potential(category)

        # Determine seasonality (event-specific logic)
        event_name = event_data.get("event", "").lower()
        is_evergreen = any(word in event_name for word in [
            "anxiety", "stress", "fear", "peace", "joy", "love"
        ])
        is_seasonal = any(word in event_name for word in [
            "christmas", "easter", "thanksgiving", "valentine"
        ])
        is_one_time = freshness_days < 3 and not is_evergreen

        seasonality_score = self.score_seasonality(is_evergreen, is_seasonal, is_one_time)
        engagement_score = self.score_engagement_signal(engagement)
        freshness_score = self.score_freshness(freshness_days)

        # Total score
        total_score = (
            search_score +
            velocity_score +
            competition_score +
            cpm_score +
            seasonality_score +
            engagement_score +
            freshness_score
        )

        result = {
            "event": event_data.get("event", "Unknown"),
            "emotion": emotion,
            "total_score": total_score,
            "breakdown": {
                "search_volume": {"score": search_score, "value": search_volume},
                "trend_velocity": {"score": velocity_score, "value": f"{trend_velocity:.1f}%"},
                "competition": {"score": competition_score, "value": competition_count},
                "cpm_potential": {"score": cpm_score, "category": category},
                "seasonality": {"score": seasonality_score, "type": "evergreen" if is_evergreen else "seasonal" if is_seasonal else "one_time"},
                "engagement": {"score": engagement_score, "value": engagement},
                "freshness": {"score": freshness_score, "days": freshness_days}
            },
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Scored opportunity: {event_data.get('event')} + {emotion} = {total_score}/100")

        return result

if __name__ == "__main__":
    # Test with sample event data
    scorer = BalancedScorer()

    sample_event = {
        "event": "AI Joblessness",
        "search_volume": 150000,
        "trend_velocity": 1500,
        "freshness_days": 1,
        "engagement": 50000
    }

    result = scorer.score_video_opportunity(sample_event, "Anxiety", "spirituality")

    import json
    print(json.dumps(result, indent=2))
