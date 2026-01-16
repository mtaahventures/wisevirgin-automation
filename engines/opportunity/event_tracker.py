"""
Event Tracker - Monitors trending events from Google Trends, news, and social media
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pytrends.request import TrendReq
import requests
from datetime import datetime, timedelta
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger("event_tracker", get_daily_log_file())

class EventTracker:
    def __init__(self):
        self.pytrends = TrendReq(hl="en-US", tz=360)
        
    def get_trending_events_google(self, geo="US", timeframe="now 7-d"):
        """Get trending events from Google Trends"""
        try:
            trending_searches = self.pytrends.trending_searches(pn=geo.lower())
            
            events = []
            for idx, keyword in enumerate(trending_searches[0].head(20).values):
                try:
                    self.pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
                    interest_data = self.pytrends.interest_over_time()
                    
                    if not interest_data.empty:
                        latest = interest_data[keyword].iloc[-1] if len(interest_data) > 0 else 0
                        earliest = interest_data[keyword].iloc[0] if len(interest_data) > 0 else 1
                        avg_interest = interest_data[keyword].mean()
                        
                        velocity = ((latest - earliest) / max(earliest, 1)) * 100
                        freshness_days = 1
                        
                        events.append({
                            "event": keyword,
                            "source": "google_trends",
                            "search_volume": int(avg_interest * 1000),
                            "trend_velocity": float(velocity),
                            "freshness_days": freshness_days,
                            "engagement": int(latest * 100),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        logger.info(f"Event tracked: {keyword} (velocity: {velocity:.1f}%)")
                        
                except Exception as e:
                    logger.warning(f"Error processing keyword {keyword}: {e}")
                    continue
                    
            return events
            
        except Exception as e:
            logger.error(f"Google Trends error: {e}")
            return []
    
    def get_news_events(self):
        """Track news events via web scraping/APIs"""
        try:
            import feedparser
            
            events = []
            news_feeds = [
                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
                "https://feeds.bbci.co.uk/news/rss.xml",
                "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            ]
            
            for feed_url in news_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:5]:
                        title = entry.get("title", "")
                        published = entry.get("published_parsed", None)
                        
                        if published:
                            pub_date = datetime(*published[:6])
                            freshness_days = (datetime.now() - pub_date).days
                        else:
                            freshness_days = 0
                        
                        events.append({
                            "event": title,
                            "source": "news_rss",
                            "search_volume": 50000,
                            "trend_velocity": 100,
                            "freshness_days": freshness_days,
                            "engagement": 10000,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing feed {feed_url}: {e}")
                    continue
            
            logger.info(f"News events tracked: {len(events)}")
            return events
            
        except Exception as e:
            logger.error(f"News tracking error: {e}")
            return []
    
    def get_social_signals(self):
        """Monitor social media signals (Twitter, Reddit)"""
        try:
            import praw
            
            events = []
            
            try:
                reddit = praw.Reddit(
                    client_id="readonly",
                    client_secret="",
                    user_agent="EventTracker/1.0"
                )
                
                subreddits = ["all", "news", "worldnews", "technology"]
                
                for subreddit_name in subreddits[:2]:
                    try:
                        subreddit = reddit.subreddit(subreddit_name)
                        
                        for post in subreddit.hot(limit=10):
                            post_age = datetime.now().timestamp() - post.created_utc
                            if post_age < 86400:
                                events.append({
                                    "event": post.title,
                                    "source": f"reddit_{subreddit_name}",
                                    "search_volume": post.score * 10,
                                    "trend_velocity": 200,
                                    "freshness_days": int(post_age / 86400),
                                    "engagement": post.num_comments + post.score,
                                    "timestamp": datetime.now().isoformat()
                                })
                    except Exception as e:
                        logger.warning(f"Reddit subreddit {subreddit_name} error: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Reddit access error: {e}")
            
            logger.info(f"Social signals tracked: {len(events)}")
            return events
            
        except Exception as e:
            logger.error(f"Social tracking error: {e}")
            return []
    
    def get_all_trending_events(self):
        """Main method: Get all trending events from all sources"""
        logger.info("Starting event tracking...")
        
        all_events = []
        
        logger.info("Fetching Google Trends events...")
        google_events = self.get_trending_events_google()
        all_events.extend(google_events)
        
        logger.info("Fetching news events...")
        news_events = self.get_news_events()
        all_events.extend(news_events)
        
        logger.info("Fetching social signals...")
        social_events = self.get_social_signals()
        all_events.extend(social_events)
        
        unique_events = []
        seen_events = set()
        
        for event in all_events:
            event_key = event["event"].lower().strip()
            if event_key not in seen_events:
                seen_events.add(event_key)
                unique_events.append(event)
        
        unique_events.sort(
            key=lambda x: x["search_volume"] * (1 + x["trend_velocity"]/100),
            reverse=True
        )
        
        logger.info(f"Event tracking complete: {len(unique_events)} unique events found")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_events": len(unique_events),
            "events": unique_events
        }

if __name__ == "__main__":
    tracker = EventTracker()
    results = tracker.get_all_trending_events()
    
    import json
    print(json.dumps(results, indent=2))
