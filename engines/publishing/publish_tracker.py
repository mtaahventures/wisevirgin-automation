"""
ENGINE 4.4: Publish Tracker
Tracks all published videos in SQLite database
Inspired by vadoo_automation tracking patterns
"""
import os
import sys
import sqlite3
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('publish_tracker', get_daily_log_file())

class PublishTracker:
    def __init__(self, db_path='data/published_videos.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                video_url TEXT NOT NULL,
                title TEXT NOT NULL,
                topic TEXT,
                publish_date TEXT NOT NULL,
                video_file TEXT,
                thumbnail_file TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                watch_time_minutes INTEGER DEFAULT 0,
                ctr_percent REAL DEFAULT 0,
                avg_view_duration REAL DEFAULT 0,
                checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f'Database initialized: {self.db_path}')
    
    def track_video(self, video_data):
        """Track a published video"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO videos 
            (video_id, video_url, title, topic, publish_date, video_file, thumbnail_file, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_data.get('video_id'),
            video_data.get('video_url'),
            video_data.get('title'),
            video_data.get('topic'),
            datetime.now().isoformat(),
            video_data.get('video_file'),
            video_data.get('thumbnail_file'),
            str(video_data.get('metadata', {}))
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f'Video tracked: {video_data.get("video_id")}')
    
    def update_performance(self, video_id, stats):
        """Update video performance stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance 
            (video_id, views, likes, comments, watch_time_minutes, ctr_percent, avg_view_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_id,
            stats.get('views', 0),
            stats.get('likes', 0),
            stats.get('comments', 0),
            stats.get('watch_time_minutes', 0),
            stats.get('ctr_percent', 0),
            stats.get('avg_view_duration', 0)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f'Performance updated for video: {video_id}')
    
    def get_all_videos(self):
        """Get all tracked videos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM videos ORDER BY created_at DESC')
        videos = cursor.fetchall()
        
        conn.close()
        
        return videos
    
    def get_video_performance(self, video_id):
        """Get performance history for a video"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM performance WHERE video_id = ? ORDER BY checked_at DESC', (video_id,))
        performance = cursor.fetchall()
        
        conn.close()
        
        return performance

if __name__ == '__main__':
    tracker = PublishTracker()
    
    # Test tracking
    test_video = {
        'video_id': 'TEST123',
        'video_url': 'https://youtube.com/watch?v=TEST123',
        'title': 'Test Video',
        'topic': 'ChatGPT for budgeting'
    }
    
    tracker.track_video(test_video)
    print("Video tracking system operational")
    
    videos = tracker.get_all_videos()
    print(f"Total videos tracked: {len(videos)}")
