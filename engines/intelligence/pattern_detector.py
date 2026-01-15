"""
ENGINE 5.2: Success Pattern Detector
Analyzes which topics/formats perform best (modular/reusable)
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engines.publishing.publish_tracker import PublishTracker
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('pattern_detector', get_daily_log_file())

class PatternDetector:
    def __init__(self):
        self.tracker = PublishTracker()
    
    def analyze_performance(self):
        """Analyze which videos performed best"""
        logger.info('Analyzing performance patterns...')
        
        videos = self.tracker.get_all_videos()
        
        if not videos:
            return {'top_topics': [], 'avg_performance': {}}
        
        # Get performance for each video
        video_performance = []
        
        for video in videos:
            video_id = video[1]
            topic = video[4]
            
            # Get latest performance
            perf = self.tracker.get_video_performance(video_id)
            
            if perf:
                latest = perf[0]  # Most recent performance record
                video_performance.append({
                    'video_id': video_id,
                    'topic': topic,
                    'views': latest[2],  # views column
                    'likes': latest[3]   # likes column
                })
        
        # Find top performing topics
        topic_stats = {}
        for vp in video_performance:
            topic = vp['topic'] or 'unknown'
            if topic not in topic_stats:
                topic_stats[topic] = {
                    'total_views': 0,
                    'total_likes': 0,
                    'video_count': 0
                }
            
            topic_stats[topic]['total_views'] += vp['views']
            topic_stats[topic]['total_likes'] += vp['likes']
            topic_stats[topic]['video_count'] += 1
        
        # Calculate averages and sort
        topic_performance = []
        for topic, stats in topic_stats.items():
            avg_views = stats['total_views'] / stats['video_count']
            topic_performance.append({
                'topic': topic,
                'avg_views': avg_views,
                'total_videos': stats['video_count']
            })
        
        topic_performance.sort(key=lambda x: x['avg_views'], reverse=True)
        
        logger.info(f'Analyzed {len(videos)} videos across {len(topic_stats)} topics')
        
        return {
            'top_topics': topic_performance[:5],
            'total_videos': len(videos)
        }

if __name__ == '__main__':
    detector = PatternDetector()
    patterns = detector.analyze_performance()
    print(f"Pattern detector ready")
    print(f"Top topics: {patterns['top_topics']}")
