"""
ENGINE 2.1: Script Research
Leverages youtube-automation-rag for best practices + scrapes top YouTube videos
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append('/root/youtube-automation-rag')

import json
from youtube_transcript_api import YouTubeTranscriptApi
from utils.youtube_api import YouTubeAPI
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('script_research', get_daily_log_file())

# Try to import RAG knowledge base
try:
    from engines.yt_knowledge_query import YTKnowledgeQuery
    RAG_AVAILABLE = True
except:
    logger.warning('YouTube Automation RAG not available, will use fallback')
    RAG_AVAILABLE = False

class ScriptResearch:
    def __init__(self):
        self.yt_api = YouTubeAPI()
        if RAG_AVAILABLE:
            try:
                self.rag = YTKnowledgeQuery()
                logger.info('RAG knowledge base loaded successfully')
            except:
                self.rag = None
                logger.warning('RAG initialization failed')
        else:
            self.rag = None
    
    def get_yt_best_practices(self, topic):
        """Get YouTube best practices from RAG knowledge base"""
        if not self.rag:
            return {
                'script_structure': 'Hook -> Problem -> Solution -> Call to Action',
                'retention_hooks': 'Add hooks every 60-90 seconds',
                'title_formula': 'How to [outcome] using [method] ([timeframe/result])'
            }
        
        try:
            # Query RAG for scripting advice
            context = self.rag.get_context('script structure retention hooks', num_results=3)
            
            # Parse and return structured advice
            return {
                'rag_context': context[:500],  # First 500 chars
                'script_structure': 'Hook -> Problem -> Solution -> Call to Action',
                'retention_hooks': 'Add pattern interrupts every 60 seconds'
            }
        except Exception as e:
            logger.error(f'RAG query error: {e}')
            return {}
    
    def scrape_top_videos(self, keyword, max_videos=5):
        """Scrape top YouTube videos on this topic"""
        try:
            # Search for top videos
            results = self.yt_api.search(keyword, max_results=max_videos, order='relevance')
            
            if 'items' not in results:
                return []
            
            top_videos = []
            
            for item in results['items']:
                video_id = item['id'].get('videoId')
                if not video_id:
                    continue
                
                video_info = {
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200],
                    'channel': item['snippet']['channelTitle']
                }
                
                # Try to get transcript
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    # Combine transcript text
                    full_text = ' '.join([t['text'] for t in transcript])
                    video_info['transcript'] = full_text[:1000]  # First 1000 chars
                    video_info['transcript_length'] = len(transcript)
                except:
                    video_info['transcript'] = None
                
                # Get video stats
                try:
                    stats = self.yt_api.get_video_stats(video_id)
                    if stats.get('items'):
                        video_stats = stats['items'][0]['statistics']
                        video_info['views'] = int(video_stats.get('viewCount', 0))
                        video_info['likes'] = int(video_stats.get('likeCount', 0))
                except:
                    pass
                
                top_videos.append(video_info)
            
            return top_videos
        
        except Exception as e:
            logger.error(f'Error scraping top videos: {e}')
            return []
    
    def research_topic(self, topic):
        """Complete research for a topic"""
        logger.info(f'Researching topic: {topic}')
        
        # Get best practices from RAG
        logger.info('Fetching YouTube best practices from RAG...')
        best_practices = self.get_yt_best_practices(topic)
        
        # Scrape top performing videos
        logger.info('Scraping top YouTube videos...')
        top_videos = self.scrape_top_videos(topic, max_videos=5)
        
        # Extract key points from top videos
        key_points = []
        for video in top_videos:
            if video.get('transcript'):
                # Extract first 200 chars as summary
                key_points.append({
                    'video_title': video['title'],
                    'snippet': video['transcript'][:200]
                })
        
        research = {
            'topic': topic,
            'best_practices': best_practices,
            'top_videos': top_videos,
            'key_points': key_points,
            'video_count': len(top_videos)
        }
        
        logger.info(f'Research complete: {len(top_videos)} videos analyzed')
        
        return research

if __name__ == '__main__':
    researcher = ScriptResearch()
    result = researcher.research_topic('ChatGPT for budgeting')
    
    print(json.dumps(result, indent=2))
