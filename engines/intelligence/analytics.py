"""
ENGINE 5.1: Performance Analytics
Fetches and analyzes video performance from YouTube API
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.youtube_api import YouTubeAPI
from engines.publishing.publish_tracker import PublishTracker
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('analytics', get_daily_log_file())

class PerformanceAnalytics:
    def __init__(self):
        self.yt_api = YouTubeAPI()
        self.tracker = PublishTracker()
    
    def fetch_video_stats(self, video_id):
        """Fetch current stats for a video"""
        try:
            stats = self.yt_api.get_video_stats(video_id)
            
            if not stats.get('items'):
                return None
            
            video_stats = stats['items'][0]['statistics']
            
            return {
                'views': int(video_stats.get('viewCount', 0)),
                'likes': int(video_stats.get('likeCount', 0)),
                'comments': int(video_stats.get('commentCount', 0))
            }
        except Exception as e:
            logger.error(f'Error fetching stats for {video_id}: {e}')
            return None
    
    def update_all_videos(self):
        """Update stats for all tracked videos"""
        logger.info('Updating stats for all videos...')
        
        videos = self.tracker.get_all_videos()
        updated_count = 0
        
        for video in videos:
            video_id = video[1]  # video_id is second column
            
            stats = self.fetch_video_stats(video_id)
            
            if stats:
                self.tracker.update_performance(video_id, stats)
                updated_count += 1
        
        logger.info(f'Updated stats for {updated_count} videos')
        
        return updated_count

if __name__ == '__main__':
    analytics = PerformanceAnalytics()
    print("Analytics engine ready")
