"""
Music Manager - Programmatic royalty-free music acquisition
For WiseVirgin meditation videos
Auto-downloads meditation music from Internet Archive if cache is empty
"""
import os
import sys
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.logging_utils import setup_logger, get_daily_log_file
from engines.production.incompetech_music_downloader import IncompetechMusicDownloader

logger = setup_logger('music_manager', get_daily_log_file())

class MusicManager:
    def __init__(self):
        self.cache_dir = 'output/cache/music'
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_peaceful_music(self, duration=300, theme='peace'):
        """
        Get peaceful background music
        1. Check for manually uploaded music
        2. Check for cached Internet Archive music
        3. Auto-download from Internet Archive if needed

        Args:
            duration: desired length in seconds
            theme: meditation theme

        Returns:
            path to music file or None
        """
        logger.info(f'Getting peaceful music for {duration}s, theme: {theme}')

        # Check for manually uploaded music first
        manual_music = os.path.join(self.cache_dir, 'peaceful_music.mp3')
        if os.path.exists(manual_music):
            logger.info(f'Using manually uploaded music: {manual_music}')
            return manual_music

        # Look for any music files in cache (excluding metadata files)
        music_files = []
        for ext in ['.mp3', '.wav', '.m4a', '.ogg']:
            for f in os.listdir(self.cache_dir):
                if f.endswith(ext) and not f.startswith('.') and not f.endswith('.txt'):
                    music_files.append(os.path.join(self.cache_dir, f))

        if music_files:
            # Use random music file
            selected = random.choice(music_files)
            logger.info(f'Using music: {selected}')
            return selected

        # No music available - auto-download from Internet Archive
        logger.warning('No music files found in cache')
        logger.info('Downloading meditation music from Internet Archive...')

        try:
            downloader = IncompetechMusicDownloader()
            tracks = downloader.download_meditation_collection()

            if tracks:
                # Use random track from downloaded collection
                selected = random.choice(tracks)
                logger.info(f'Using downloaded music: {selected}')
                return selected
            else:
                logger.error('Failed to download meditation music')
                return None

        except Exception as e:
            logger.error(f'Error downloading music: {e}')
            return None

if __name__ == '__main__':
    manager = MusicManager()
    music = manager.get_peaceful_music(duration=300, theme='peace and rest')
    if music:
        print(f'Music: {music}')
    else:
        print('No music available')
        print(f'Add music files to: {manager.cache_dir}')
