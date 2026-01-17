"""
Opportunity Selector - Smart selection with fallback

Tries to detect trending events, falls back to high-value curated opportunities
"""
import os
import json
from datetime import datetime
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger("opportunity_selector", get_daily_log_file())

# High-value curated opportunities (fallback when tracking fails)
CURATED_OPPORTUNITIES = [
    {"event": "AI Joblessness", "emotion": "Anxiety", "content_type": "negative", "score": 93},
    {"event": "Economic Uncertainty", "emotion": "Fear", "content_type": "negative", "score": 91},
    {"event": "Climate Change", "emotion": "Hope", "content_type": "positive", "score": 89},
    {"event": "Political Division", "emotion": "Peace", "content_type": "positive", "score": 87},
    {"event": "Health Crisis", "emotion": "Comfort", "content_type": "positive", "score": 86},
    {"event": "Social Media Anxiety", "emotion": "Peace", "content_type": "positive", "score": 85},
    {"event": "Financial Stress", "emotion": "Trust", "content_type": "positive", "score": 84},
    {"event": "Relationship Breakdown", "emotion": "Hope", "content_type": "positive", "score": 83},
    {"event": "Career Uncertainty", "emotion": "Faith", "content_type": "positive", "score": 82},
    {"event": "Mental Health Struggles", "emotion": "Comfort", "content_type": "positive", "score": 81},
]

USAGE_FILE = "data/opportunity_usage.json"

def load_usage_history():
    """Load usage history to avoid repetition"""
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_usage(opportunity):
    """Record opportunity usage"""
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)

    history = load_usage_history()
    key = f"{opportunity['event']}_{opportunity['emotion']}"

    if key not in history:
        history[key] = []

    history[key].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat()
    })

    with open(USAGE_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_best_opportunity(format_name="shorts", prefer_new=True):
    """
    Get best opportunity for the format

    Args:
        format_name: shorts, medium, extended, or sleep
        prefer_new: If True, prefer opportunities not used recently

    Returns:
        dict: Selected opportunity
    """
    logger.info(f"Selecting opportunity for {format_name}...")

    # Try to detect trending events first
    try:
        from engines.opportunity.event_tracker import EventTracker
        from engines.opportunity.balanced_scorer import BalancedScorer

        tracker = EventTracker()
        scorer = BalancedScorer()

        events = tracker.get_all_trending_events()

        if events and len(events) > 0:
            logger.info(f"Found {len(events)} trending events")

            # Score top events
            best_score = 0
            best_opportunity = None

            for event in events[:3]:
                scores = scorer.score_event_emotions(
                    event=event['event'],
                    emotions_list=['anxiety', 'fear', 'hope', 'peace', 'comfort', 'stress']
                )

                for score_data in scores:
                    if score_data['total_score'] > best_score:
                        best_score = score_data['total_score']
                        best_opportunity = {
                            'event': event['event'],
                            'emotion': score_data['emotion'],
                            'content_type': score_data['content_type'],
                            'score': score_data['total_score']
                        }

            if best_opportunity:
                logger.info(f"✅ Detected opportunity: {best_opportunity['event']} + {best_opportunity['emotion']} (score: {best_opportunity['score']})")
                save_usage(best_opportunity)
                return best_opportunity

    except Exception as e:
        logger.warning(f"Event tracking failed: {e}")

    # Fallback to curated opportunities
    logger.info("Using curated opportunities (fallback)")

    history = load_usage_history()
    today = datetime.now().strftime("%Y-%m-%d")

    # Find least recently used opportunity
    best_opportunity = None
    oldest_date = datetime.now()

    for opp in CURATED_OPPORTUNITIES:
        key = f"{opp['event']}_{opp['emotion']}"

        if key not in history:
            # Never used - perfect!
            best_opportunity = opp
            break

        # Check if used today
        used_today = any(use['date'] == today for use in history[key])
        if used_today:
            continue

        # Find oldest usage
        last_use = max(history[key], key=lambda x: x['timestamp'])
        last_use_date = datetime.fromisoformat(last_use['timestamp'])

        if last_use_date < oldest_date:
            oldest_date = last_use_date
            best_opportunity = opp

    if not best_opportunity:
        # All used today, just use first one
        best_opportunity = CURATED_OPPORTUNITIES[0]

    logger.info(f"✅ Selected: {best_opportunity['event']} + {best_opportunity['emotion']} (score: {best_opportunity['score']})")
    save_usage(best_opportunity)
    return best_opportunity
