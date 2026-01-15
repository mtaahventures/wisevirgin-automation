"""
Incompetech Music Downloader - Programmatic royalty-free music acquisition
Downloads Kevin MacLeod's meditation music from Internet Archive
License: CC-BY 4.0 (YouTube monetization safe with attribution)
"""
import os
import sys
import requests
import zipfile
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('incompetech_downloader', get_daily_log_file())

class IncompetechMusicDownloader:
    def __init__(self):
        self.archive_url = 'https://archive.org/download/incompetech-all-the-music-2020'
        self.cache_dir = 'output/cache/music'
        self.temp_dir = 'output/cache/temp'
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def download_meditation_collection(self):
        """
        Download meditation/ambient music from Internet Archive
        Kevin MacLeod's Incompetech collection (CC-BY 4.0)
        """
        logger.info('Downloading meditation music from Internet Archive...')
        logger.info('Source: Kevin MacLeod - Incompetech (CC-BY 4.0)')

        # Meditation-related zip files from the collection
        # Kevin MacLeod's complete collection split into A-F
        # Starting with A (1.48 GB) to extract meditation tracks
        target_files = [
            'Incompetech - All the Music - 2020 A 180122.mp3.zip',
        ]

        downloaded_tracks = []

        for zip_filename in target_files:
            zip_url = f'{self.archive_url}/{zip_filename}'
            local_zip = os.path.join(self.temp_dir, zip_filename)

            # Check if already downloaded
            if os.path.exists(local_zip):
                logger.info(f'Using cached archive: {zip_filename}')
            else:
                logger.info(f'Downloading: {zip_filename} (~1.5GB, may take 5-10 minutes)')

                try:
                    response = requests.get(zip_url, stream=True, timeout=300)
                    response.raise_for_status()

                    total_size = int(response.headers.get('content-length', 0))
                    block_size = 8192
                    downloaded = 0

                    with open(local_zip, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=block_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    if downloaded % (block_size * 100) == 0:  # Log every 800KB
                                        logger.info(f'Download progress: {percent:.1f}%')

                    logger.info(f'✅ Downloaded: {zip_filename}')

                except Exception as e:
                    logger.error(f'Failed to download {zip_filename}: {e}')
                    continue

            # Extract meditation tracks
            logger.info(f'Extracting meditation tracks from {zip_filename}...')
            extracted = self._extract_meditation_tracks(local_zip)
            downloaded_tracks.extend(extracted)

        if downloaded_tracks:
            logger.info(f'✅ Successfully extracted {len(downloaded_tracks)} meditation tracks')
            logger.info('License: CC-BY 4.0 - Attribution required')
            logger.info('Attribution: Music by Kevin MacLeod (incompetech.com)')
            return downloaded_tracks
        else:
            logger.warning('No meditation tracks extracted')
            return []

    def _extract_meditation_tracks(self, zip_path):
        """Extract meditation/ambient/calming tracks from zip"""
        meditation_keywords = [
            'meditation', 'calm', 'peaceful', 'ambient', 'serene',
            'tranquil', 'zen', 'relax', 'soothing', 'gentle',
            'soft', 'quiet', 'rest', 'peace', 'still'
        ]

        extracted_tracks = []

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                for file_info in zip_file.filelist:
                    filename = file_info.filename.lower()

                    # Check if it's an MP3 file with meditation keywords
                    if filename.endswith('.mp3'):
                        if any(keyword in filename for keyword in meditation_keywords):
                            # Extract to music cache
                            output_path = os.path.join(
                                self.cache_dir,
                                os.path.basename(file_info.filename)
                            )

                            # Skip if already extracted
                            if os.path.exists(output_path):
                                logger.debug(f'Already extracted: {os.path.basename(file_info.filename)}')
                                extracted_tracks.append(output_path)
                                continue

                            # Extract the file
                            zip_file.extract(file_info, self.temp_dir)

                            # Move to music cache
                            temp_path = os.path.join(self.temp_dir, file_info.filename)
                            if os.path.exists(temp_path):
                                os.rename(temp_path, output_path)
                                extracted_tracks.append(output_path)
                                logger.info(f'Extracted: {os.path.basename(output_path)}')

        except Exception as e:
            logger.error(f'Error extracting tracks: {e}')

        return extracted_tracks

    def download_specific_tracks(self):
        """
        Download specific meditation tracks directly (faster than full archive)
        Uses Internet Archive's direct file access
        """
        logger.info('Downloading specific meditation tracks...')

        # Direct links to meditation tracks on Internet Archive
        meditation_tracks = [
            'Kevin_MacLeod_-_Meditation_Impromptu_01.mp3',
            'Kevin_MacLeod_-_Meditation_Impromptu_02.mp3',
            'Kevin_MacLeod_-_Meditation_Impromptu_03.mp3',
            'Kevin_MacLeod_-_Pastoral.mp3',
            'Kevin_MacLeod_-_Relaxing.mp3',
        ]

        downloaded = []

        for track_name in meditation_tracks:
            output_path = os.path.join(self.cache_dir, track_name)

            if os.path.exists(output_path):
                logger.info(f'Already have: {track_name}')
                downloaded.append(output_path)
                continue

            # Try to download from archive
            track_url = f'{self.archive_url}/{track_name}'

            try:
                logger.info(f'Downloading: {track_name}')
                response = requests.get(track_url, timeout=60)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                logger.info(f'✅ Downloaded: {track_name} ({file_size:.1f} MB)')
                downloaded.append(output_path)

            except Exception as e:
                logger.warning(f'Could not download {track_name}: {e}')

        return downloaded

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print('🎵 Incompetech Music Downloader\n')
    print('=' * 60)
    print('Source: Kevin MacLeod - Internet Archive')
    print('License: CC-BY 4.0 (YouTube monetization safe)')
    print('Attribution required: Music by Kevin MacLeod (incompetech.com)')
    print('=' * 60)
    print()

    downloader = IncompetechMusicDownloader()

    # Try specific tracks first (faster)
    print('Attempting to download specific meditation tracks...\n')
    tracks = downloader.download_specific_tracks()

    if tracks:
        print(f'\n✅ SUCCESS! Downloaded {len(tracks)} meditation tracks')
        print('\nTracks available:')
        for track in tracks:
            print(f'  - {os.path.basename(track)}')
        print('\n📝 Remember to add attribution in video description:')
        print('   "Music by Kevin MacLeod (incompetech.com)"')
        print('   "Licensed under Creative Commons: By Attribution 4.0"')
    else:
        print('\n⏸️  Specific tracks not available, would need full archive download')
        print('Full archive is ~1.5GB and will take 5-10 minutes')
        print('Run with full_archive=True to download complete collection')
