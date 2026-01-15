"""
ENGINE 1.1: Trend Monitor
Scrapes Google Trends, Product Hunt, Reddit for trending Personal Finance + AI topics
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from pytrends.request import TrendReq
import praw
import feedparser
import requests
from datetime import datetime, timedelta
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('trend_monitor', get_daily_log_file())

class TrendMonitor:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        # Reddit setup (read-only, no auth needed for public posts)
        self.reddit = praw.Reddit(
            client_id='your_client_id_here',  # Will use read-only mode
            client_secret='your_secret_here',
            user_agent='SmartMoneyAutomation/1.0'
        )
        
    def get_google_trends(self, keywords):
        """Get Google Trends data for keywords"""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='US')
            interest_over_time = self.pytrends.interest_over_time()
            
            if interest_over_time.empty:
                return []
            
            # Get related queries
            related = self.pytrends.related_queries()
            
            trends = []
            for keyword in keywords:
                if keyword in interest_over_time.columns:
                    avg_interest = interest_over_time[keyword].mean()
                    latest_interest = interest_over_time[keyword].iloc[-1]
                    
                    # Calculate trend velocity
                    week_ago = interest_over_time[keyword].iloc[0] if len(interest_over_time) > 0 else 1
                    velocity = ((latest_interest - week_ago) / max(week_ago, 1)) * 100
                    
                    trends.append({
                        'keyword': keyword,
                        'avg_interest': float(avg_interest),
                        'current_interest': float(latest_interest),
                        'velocity_pct': float(velocity),
                        'related_queries': related.get(keyword, {}).get('rising', [])[:5] if related else []
                    })
            
            return trends
        except Exception as e:
            logger.error(f'Google Trends error: {e}')
            return []
    
    def get_reddit_trends(self, subreddits=['personalfinance', 'artificial', 'ChatGPT', 'OpenAI']):
        """Get trending topics from finance + AI subreddits"""
        try:
            trending_topics = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    # Get top posts from last 24 hours
                    for post in subreddit.hot(limit=10):
                        if post.created_utc > (datetime.now().timestamp() - 86400):  # Last 24h
                            trending_topics.append({
                                'title': post.title,
                                'subreddit': subreddit_name,
                                'score': post.score,
                                'url': post.url,
                                'created': datetime.fromtimestamp(post.created_utc).isoformat()
                            })
                except Exception as e:
                    logger.warning(f'Reddit subreddit {subreddit_name} error: {e}')
                    continue
            
            # Sort by score
            trending_topics.sort(key=lambda x: x['score'], reverse=True)
            return trending_topics[:20]
        
        except Exception as e:
            logger.error(f'Reddit trends error: {e}')
            return []
    
    def get_product_hunt_ai_tools(self):
        """Get trending AI tools from Product Hunt RSS"""
        try:
            # Product Hunt AI category RSS
            feed_url = 'https://www.producthunt.com/feed/topic/artificial-intelligence'
            feed = feedparser.parse(feed_url)
            
            ai_tools = []
            for entry in feed.entries[:10]:
                ai_tools.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else None,
                    'summary': entry.summary if hasattr(entry, 'summary') else ''
                })
            
            return ai_tools
        except Exception as e:
            logger.error(f'Product Hunt error: {e}')
            return []
    
    def find_opportunities(self):
        """Main method: Find all trending opportunities"""
        logger.info('Starting trend monitoring...')
        
        # Define Personal Finance + AI keywords
        finance_keywords = [
            'personal finance ai',
            'chatgpt budgeting',
            'ai investing',
            'chatgpt financial advice',
            'ai money management'
        ]
        
        # Get Google Trends
        logger.info('Fetching Google Trends...')
        google_trends = self.get_google_trends(finance_keywords)
        
        # Get Reddit trends
        logger.info('Fetching Reddit trends...')
        reddit_trends = self.get_reddit_trends()
        
        # Get Product Hunt AI tools
        logger.info('Fetching Product Hunt AI tools...')
        product_hunt_tools = self.get_product_hunt_ai_tools()
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'google_trends': google_trends,
            'reddit_trends': reddit_trends,
            'product_hunt_tools': product_hunt_tools
        }
        
        logger.info(f'Trend monitoring complete: {len(google_trends)} Google trends, {len(reddit_trends)} Reddit posts, {len(product_hunt_tools)} PH tools')
        
        return results

if __name__ == '__main__':
    monitor = TrendMonitor()
    results = monitor.find_opportunities()
    
    import json
    print(json.dumps(results, indent=2))
