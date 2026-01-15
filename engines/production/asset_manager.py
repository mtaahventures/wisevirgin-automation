"""
ENGINE 3.2: Visual Asset Manager
Downloads stock footage from Pexels (free API)
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import requests
import random
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('asset_manager', get_daily_log_file())

class AssetManager:
    def __init__(self, api_key=None):
        # Pexels free API key (get from https://www.pexels.com/api/)
        self.api_key = api_key or os.getenv('PEXELS_API_KEY', 'YOUR_PEXELS_KEY_HERE')
        self.api_url = 'https://api.pexels.com/videos/search'
        self.headers = {'Authorization': self.api_key}
    
    def search_videos(self, query, per_page=15):
        """Search for stock videos on Pexels"""
        try:
            params = {
                'query': query,
                'per_page': per_page,
                'orientation': 'landscape'
            }
            
            response = requests.get(self.api_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('videos', [])
            else:
                logger.warning(f'Pexels API error: {response.status_code}')
                return []
        except Exception as e:
            logger.error(f'Error searching Pexels: {e}')
            return []
    
    def download_video(self, video_url, output_path):
        """Download a video file"""
        try:
            response = requests.get(video_url, stream=True)
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f'Downloaded: {output_path}')
                return output_path
            else:
                logger.error(f'Download failed: {response.status_code}')
                return None
        except Exception as e:
            logger.error(f'Download error: {e}')
            return None
    
    def get_assets_for_topic(self, topic, num_clips=20):
        """Get relevant stock footage for a topic"""
        logger.info(f'Fetching assets for topic: {topic}')
        
        # Extract keywords from topic
        keywords = [
            'money',
            'finance',
            'computer',
            'technology',
            'office',
            'business'
        ]
        
        # Add AI-specific keywords if relevant
        if 'ai' in topic.lower() or 'chatgpt' in topic.lower():
            keywords.extend(['artificial intelligence', 'technology', 'computer screen'])
        
        if 'budget' in topic.lower():
            keywords.extend(['calculator', 'spreadsheet', 'planning'])
        
        # Search and collect videos
        all_videos = []
        for keyword in keywords[:3]:  # Limit API calls
            videos = self.search_videos(keyword, per_page=5)
            all_videos.extend(videos)
        
        # Download best quality videos
        downloaded = []
        output_dir = 'output/cache/stock_footage'
        
        for i, video in enumerate(all_videos[:num_clips]):
            try:
                # Get HD video file
                video_files = video.get('video_files', [])
                hd_file = next((f for f in video_files if f.get('quality') == 'hd'), None)
                
                if not hd_file:
                    hd_file = video_files[0] if video_files else None
                
                if hd_file:
                    video_url = hd_file['link']
                    output_file = os.path.join(output_dir, f'clip_{i+1}.mp4')
                    
                    if os.path.exists(output_file):
                        logger.info(f'Using cached clip: {output_file}')
                        downloaded.append(output_file)
                    else:
                        result = self.download_video(video_url, output_file)
                        if result:
                            downloaded.append(result)
            except Exception as e:
                logger.warning(f'Error processing video {i}: {e}')
                continue
        
        logger.info(f'Downloaded {len(downloaded)} video clips')
        
        return downloaded

if __name__ == '__main__':
    manager = AssetManager()
    clips = manager.get_assets_for_topic('ChatGPT for budgeting', num_clips=5)
    print(f"Downloaded {len(clips)} clips")
    for clip in clips:
        print(f"  - {clip}")
