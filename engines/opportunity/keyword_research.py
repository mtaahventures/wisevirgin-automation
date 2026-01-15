"""
ENGINE 1.2: Keyword Research
Analyzes YouTube search patterns and competition
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
from utils.youtube_api import YouTubeAPI
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('keyword_research', get_daily_log_file())

class KeywordResearch:
    def __init__(self):
        self.yt_api = YouTubeAPI()
        
    def get_youtube_autocomplete(self, query):
        """Get YouTube autocomplete suggestions"""
        try:
            url = 'https://suggestqueries.google.com/complete/search'
            params = {
                'client': 'youtube',
                'ds': 'yt',
                'q': query
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                # Response is JSONP, extract JSON part
                data = response.text
                # Remove callback wrapper
                data = data[data.index('(')+1:data.rindex(')')]
                import json
                suggestions = json.loads(data)[1]
                return [s[0] for s in suggestions]
            return []
        except Exception as e:
            logger.error(f'Autocomplete error: {e}')
            return []
    
    def analyze_competition(self, keyword):
        """Analyze competition for a keyword"""
        try:
            # Search YouTube for this keyword
            results = self.yt_api.search(keyword, max_results=10)
            
            if 'items' not in results:
                return {
                    'keyword': keyword,
                    'video_count': 0,
                    'competition': 'unknown'
                }
            
            video_count = len(results['items'])
            
            # Estimate competition level
            if video_count < 5:
                competition = 'low'
            elif video_count < 15:
                competition = 'medium'
            else:
                competition = 'high'
            
            # Get top video stats
            top_videos = []
            for item in results['items'][:5]:
                video_id = item['id'].get('videoId')
                if video_id:
                    try:
                        stats = self.yt_api.get_video_stats(video_id)
                        if stats.get('items'):
                            video_stats = stats['items'][0]['statistics']
                            top_videos.append({
                                'title': item['snippet']['title'],
                                'views': int(video_stats.get('viewCount', 0)),
                                'likes': int(video_stats.get('likeCount', 0))
                            })
                    except:
                        continue
            
            return {
                'keyword': keyword,
                'video_count': video_count,
                'competition': competition,
                'top_videos': top_videos
            }
        except Exception as e:
            logger.error(f'Competition analysis error for {keyword}: {e}')
            return {
                'keyword': keyword,
                'video_count': 0,
                'competition': 'unknown',
                'error': str(e)
            }
    
    def research_topic(self, base_keyword):
        """Complete keyword research for a topic"""
        logger.info(f'Researching keyword: {base_keyword}')
        
        # Get autocomplete variations
        suggestions = self.get_youtube_autocomplete(base_keyword)
        
        # Analyze base keyword
        base_analysis = self.analyze_competition(base_keyword)
        
        # Analyze top 3 suggestions
        suggestion_analysis = []
        for suggestion in suggestions[:3]:
            analysis = self.analyze_competition(suggestion)
            suggestion_analysis.append(analysis)
        
        return {
            'base_keyword': base_keyword,
            'base_analysis': base_analysis,
            'suggestions': suggestions,
            'suggestion_analysis': suggestion_analysis
        }

if __name__ == '__main__':
    researcher = KeywordResearch()
    result = researcher.research_topic('chatgpt for budgeting')
    
    import json
    print(json.dumps(result, indent=2))
