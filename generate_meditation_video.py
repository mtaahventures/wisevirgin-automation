#!/usr/bin/env python3
"""
Generate Complete Meditation Video Test
Tests full pipeline: Scripture + Nature + Music + Assembly
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/root/wisevirgin')

from utils.logging_utils import setup_logger
from engines.content.scripture_generator import ScriptureGenerator
from engines.production.nature_asset_manager import NatureAssetManager
from engines.production.music_manager import MusicManager
from engines.production.meditation_video_assembler import MeditationVideoAssembler

logger = setup_logger('meditation_video_test')

def generate_meditation_video(theme='peace and rest', duration=60, verse_count=3):
    """Generate a complete meditation video"""

    logger.info('='*60)
    logger.info(f'Generating Meditation Video: {theme}')
    logger.info(f'Duration: {duration}s | Verses: {verse_count}')
    logger.info('='*60)

    # Step 1: Generate scriptures
    logger.info('\n1. Generating scripture verses...')
    scripture_gen = ScriptureGenerator()
    scripture_result = scripture_gen.generate_scripture_collection(theme, verse_count)

    if not scripture_result or not scripture_result.get('verses'):
        logger.error('Failed to generate scriptures')
        return False

    scriptures = scripture_result['verses']
    logger.info(f'   ✅ Generated {len(scriptures)} verses')
    for i, verse in enumerate(scriptures[:2], 1):
        logger.info(f'   {i}. {verse[:60]}...')

    # Step 2: Get nature videos
    logger.info('\n2. Fetching nature footage...')
    nature_mgr = NatureAssetManager()
    nature_videos = nature_mgr.fetch_nature_videos('peaceful nature', count=5)

    if not nature_videos:
        logger.error('Failed to fetch nature videos')
        return False

    logger.info(f'   ✅ Fetched {len(nature_videos)} nature videos')

    # Step 3: Get music
    logger.info('\n3. Getting peaceful music...')
    music_mgr = MusicManager()
    music_file = music_mgr.get_peaceful_music(duration=duration, theme=theme)

    if not music_file:
        logger.warning('   ⚠️  No music available - video will be silent')
    else:
        logger.info(f'   ✅ Music: {os.path.basename(music_file)}')

    # Step 4: Assemble video
    logger.info('\n4. Assembling meditation video...')
    assembler = MeditationVideoAssembler()

    try:
        video_file = assembler.assemble_meditation_video(
            nature_videos=nature_videos,
            scriptures=scriptures,
            music_file=music_file,
            duration=duration
        )

        if video_file and os.path.exists(video_file):
            file_size = os.path.getsize(video_file) / (1024 * 1024)  # MB
            logger.info(f'   ✅ Video created: {video_file}')
            logger.info(f'   Size: {file_size:.1f} MB')

            logger.info('\n' + '='*60)
            logger.info('SUCCESS! Meditation video generated!')
            logger.info('='*60)
            logger.info(f'Video: {video_file}')
            logger.info('Attribution: Music by Kevin MacLeod (incompetech.com)')
            logger.info('License: CC-BY 4.0')
            logger.info('='*60)

            return video_file
        else:
            logger.error('Video assembly failed')
            return False

    except Exception as e:
        logger.error(f'Error assembling video: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate meditation video')
    parser.add_argument('--theme', default='peace and rest', help='Meditation theme')
    parser.add_argument('--duration', type=int, default=60, help='Video duration in seconds')
    parser.add_argument('--verses', type=int, default=3, help='Number of scripture verses')

    args = parser.parse_args()

    result = generate_meditation_video(
        theme=args.theme,
        duration=args.duration,
        verse_count=args.verses
    )

    if result:
        print(f'\n✅ Success! Video: {result}')
    else:
        print('\n❌ Failed to generate video')
        sys.exit(1)
