"""
Nature Asset Manager - Downloads beautiful nature stock videos for meditation
"""
import os
import requests
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('nature_assets', get_daily_log_file())

class NatureAssetManager:
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.cache_dir = 'output/cache/nature_footage'
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_nature_videos(self, theme='peaceful nature', count=15):
        """
        Fetch beautiful nature videos from Pexels
        theme: search query for nature videos
        count: number of videos to download
        """
        logger.info(f'Fetching {count} nature videos: {theme}')

        # Check cache
        cached_videos = [
            os.path.join(self.cache_dir, f)
            for f in os.listdir(self.cache_dir)
            if f.endswith('.mp4')
        ]

        if len(cached_videos) >= count:
            logger.info(f'Using {count} cached nature videos')
            return cached_videos[:count]

        if not self.pexels_key or self.pexels_key == 'YOUR_PEXELS_API_KEY':
            logger.error('No Pexels API key configured')
            return cached_videos if cached_videos else []

        # Nature-themed search queries
        nature_queries = [
            'peaceful river flowing',
            'beautiful forest nature',
            'ocean waves peaceful',
            'mountain landscape serene',
            'sunset nature beautiful',
            'lake reflection calm',
            'waterfall nature',
            'meadow flowers peaceful',
            'birds flying nature',
            'clouds sky peaceful'
        ]

        try:
            downloaded_videos = []
            query_idx = 0

            while len(downloaded_videos) < count and query_idx < len(nature_queries):
                query = nature_queries[query_idx]
                logger.info(f'Searching Pexels: {query}')

                url = 'https://api.pexels.com/videos/search'
                headers = {'Authorization': self.pexels_key}
                params = {
                    'query': query,
                    'per_page': 5,
                    'orientation': 'landscape',
                    'size': 'medium'
                }

                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get('videos'):
                    for video in data['videos']:
                        if len(downloaded_videos) >= count:
                            break

                        # Get HD video file
                        video_files = video.get('video_files', [])
                        hd_video = next(
                            (v for v in video_files if v.get('quality') == 'hd'),
                            video_files[0] if video_files else None
                        )

                        if hd_video:
                            video_url = hd_video['link']
                            output_file = os.path.join(
                                self.cache_dir,
                                f'nature_{len(downloaded_videos) + 1}.mp4'
                            )

                            if not os.path.exists(output_file):
                                logger.info(f'Downloading nature video {len(downloaded_videos) + 1}...')
                                video_response = requests.get(video_url, stream=True, timeout=30)
                                video_response.raise_for_status()

                                with open(output_file, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)

                            downloaded_videos.append(output_file)

                query_idx += 1

            logger.info(f'Downloaded {len(downloaded_videos)} nature videos')
            return downloaded_videos + cached_videos[:count - len(downloaded_videos)]

        except Exception as e:
            logger.error(f'Error fetching nature videos: {e}')
            return cached_videos if cached_videos else []

if __name__ == '__main__':
    manager = NatureAssetManager()
    videos = manager.fetch_nature_videos('peaceful nature', 10)
    print(f'Found {len(videos)} nature videos')
    for v in videos:
        print(f'  {v}')
