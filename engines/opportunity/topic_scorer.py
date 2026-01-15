"""
ENGINE 1.4: Topic Scorer
Combines trend data + keyword research to score and select best topic
"""
import os
import sys
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engines.opportunity.trend_monitor import TrendMonitor
from engines.opportunity.keyword_research import KeywordResearch
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('topic_scorer', get_daily_log_file())

class TopicScorer:
    def __init__(self):
        self.trend_monitor = TrendMonitor()
        self.keyword_researcher = KeywordResearch()
        
    def score_opportunity(self, keyword, trend_data=None, keyword_data=None):
        """Score a single opportunity (0-100)"""
        score = 0
        factors = {}
        
        # Factor 1: Trend Velocity (0-30 points)
        if trend_data and 'velocity_pct' in trend_data:
            velocity = trend_data['velocity_pct']
            if velocity > 100:
                trend_score = 30
            elif velocity > 50:
                trend_score = 20
            elif velocity > 0:
                trend_score = 10
            else:
                trend_score = 5
            score += trend_score
            factors['trend_velocity'] = trend_score
        
        # Factor 2: Search Interest (0-25 points)
        if trend_data and 'current_interest' in trend_data:
            interest = trend_data['current_interest']
            if interest > 75:
                interest_score = 25
            elif interest > 50:
                interest_score = 20
            elif interest > 25:
                interest_score = 15
            else:
                interest_score = 10
            score += interest_score
            factors['search_interest'] = interest_score
        
        # Factor 3: Competition Level (0-25 points) - Lower competition = higher score
        if keyword_data and 'competition' in keyword_data:
            comp = keyword_data['competition']
            if comp == 'low':
                comp_score = 25
            elif comp == 'medium':
                comp_score = 15
            elif comp == 'high':
                comp_score = 5
            else:
                comp_score = 10
            score += comp_score
            factors['competition'] = comp_score
        
        # Factor 4: Recency Bonus (0-20 points)
        # New topics get bonus points
        recency_score = 15  # Default for recent topics
        score += recency_score
        factors['recency'] = recency_score
        
        return {
            'keyword': keyword,
            'total_score': score,
            'factors': factors
        }
    
    def find_best_topic(self):
        """Main method: Find the best video topic for today"""
        logger.info('Finding best topic for today...')
        
        # Step 1: Get trending data
        logger.info('Step 1: Gathering trend data...')
        trends = self.trend_monitor.find_opportunities()
        
        # Step 2: Extract potential keywords
        keywords = []
        
        # From Google Trends
        for trend in trends.get('google_trends', []):
            keywords.append({
                'keyword': trend['keyword'],
                'source': 'google_trends',
                'trend_data': trend
            })
        
        # From Reddit (extract keywords from top posts)
        for reddit_post in trends.get('reddit_trends', [])[:5]:
            # Simple keyword extraction from title
            title = reddit_post['title'].lower()
            if 'ai' in title or 'chatgpt' in title or 'finance' in title or 'budget' in title:
                keywords.append({
                    'keyword': reddit_post['title'][:50],  # Truncate long titles
                    'source': 'reddit',
                    'trend_data': {'score': reddit_post['score']}
                })
        
        # From Product Hunt (AI tools)
        for tool in trends.get('product_hunt_tools', [])[:3]:
            keywords.append({
                'keyword': f"how to use {tool['title']}",
                'source': 'product_hunt',
                'trend_data': tool
            })
        
        # Step 3: Research and score each keyword
        logger.info(f'Step 2: Scoring {len(keywords)} opportunities...')
        scored_topics = []
        
        for kw in keywords[:10]:  # Limit to top 10 to avoid API quota
            keyword = kw['keyword']
            trend_data = kw.get('trend_data', {})
            
            # Get keyword research data
            try:
                keyword_data = self.keyword_researcher.analyze_competition(keyword)
            except:
                keyword_data = {}
            
            # Score this opportunity
            score_result = self.score_opportunity(keyword, trend_data, keyword_data)
            score_result['source'] = kw['source']
            score_result['keyword_data'] = keyword_data
            
            scored_topics.append(score_result)
        
        # Step 4: Sort by score and select best
        scored_topics.sort(key=lambda x: x['total_score'], reverse=True)
        
        if scored_topics:
            best_topic = scored_topics[0]
            logger.info(f'Best topic selected: {best_topic["keyword"]} (score: {best_topic["total_score"]})')
        else:
            # Fallback to a default finance + AI topic
            logger.warning('No topics found, using rotating fallback')
            
            # Rotating fallback topics - Personal Finance + AI blend
            fallback_topics = [
                'ChatGPT for budgeting tutorial',
                'AI tools for tracking expenses',
                'ChatGPT prompts for saving money',
                'Using AI to analyze bank statements',
                'ChatGPT for debt payoff planning',
                'AI-powered investment research',
                'ChatGPT for retirement planning',
                'Automate finances with ChatGPT',
                'AI tools for credit score improvement',
                'ChatGPT for side hustle ideas',
                'Using AI to negotiate bills',
                'ChatGPT for tax optimization',
                'AI personal finance assistant setup',
                'ChatGPT prompts for wealth building',
                'AI tools for passive income ideas',
                'ChatGPT for emergency fund planning',
                'Using AI to find better insurance rates',
                'ChatGPT for college savings planning',
                'AI-powered budget forecasting',
                'ChatGPT for financial goal setting',
                'AI tools for expense categorization',
                'ChatGPT for investment portfolio review',
                'Using AI to reduce monthly bills',
                'ChatGPT prompts for frugal living',
                'AI tools for subscription management',
                'ChatGPT for meal planning on a budget',
                'Using AI to maximize credit card rewards',
                'ChatGPT for real estate investing research',
                'AI-powered net worth tracking',
                'ChatGPT for financial literacy education'
            ]
            
            # Use day of year to rotate through topics
            from datetime import datetime as dt
            day_of_year = dt.now().timetuple().tm_yday
            topic_index = day_of_year % len(fallback_topics)
            selected_topic = fallback_topics[topic_index]
            
            logger.info(f'Using fallback topic {topic_index + 1}/{len(fallback_topics)}: {selected_topic}')
            
            best_topic = {
                'keyword': selected_topic,
                'total_score': 50,
                'source': 'fallback_rotating',
                'factors': {},
                'keyword_data': {}
            }
        
        # Save result
        result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'best_topic': best_topic,
            'all_scored_topics': scored_topics
        }
        
        # Save to data directory
        output_file = 'data/daily_opportunity.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f'Results saved to {output_file}')
        
        return result

if __name__ == '__main__':
    scorer = TopicScorer()
    result = scorer.find_best_topic()
    
    print(f"\n=== BEST TOPIC FOR TODAY ===")
    print(f"Topic: {result['best_topic']['keyword']}")
    print(f"Score: {result['best_topic']['total_score']}/100")
    print(f"Source: {result['best_topic']['source']}")
    print(f"\nScore Breakdown:")
    for factor, points in result['best_topic']['factors'].items():
        print(f"  {factor}: {points} points")
