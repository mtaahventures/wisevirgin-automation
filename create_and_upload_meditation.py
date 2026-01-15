#!/usr/bin/env python3
"""
Create and Upload Meditation Video to YouTube
Full end-to-end pipeline: Generate -> Upload -> Return URL
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('/root/wisevirgin')

from utils.logging_utils import setup_logger
from engines.content.scripture_generator import ScriptureGenerator
from engines.content.seo_generator import SEOGenerator
from engines.production.nature_asset_manager import NatureAssetManager
from engines.production.music_manager import MusicManager
from engines.production.meditation_video_assembler import MeditationVideoAssembler
from engines.publishing.youtube_uploader import YouTubeUploader

logger = setup_logger('meditation_youtube')

def create_and_upload_meditation_video(theme='peace and rest', duration=300, verse_count=8):
    """Generate meditation video and upload to YouTube"""

    logger.info('='*70)
    logger.info('CREATING & UPLOADING MEDITATION VIDEO TO YOUTUBE')
    logger.info('='*70)
    logger.info(f'Theme: {theme}')
    logger.info(f'Duration: {duration}s ({duration/60:.1f} minutes)')
    logger.info(f'Verses: {verse_count}')
    logger.info('='*70)

    # Step 1: Generate scripture verses
    logger.info('\n1️⃣  Generating scripture verses...')
    scripture_gen = ScriptureGenerator()
    scripture_result = scripture_gen.generate_scripture_collection(theme, verse_count)

    if not scripture_result or not scripture_result.get('verses'):
        logger.error('Failed to generate scriptures')
        return None

    scriptures = scripture_result['verses']
    logger.info(f'   ✅ Generated {len(scriptures)} verses')

    # Step 2: Get nature videos
    logger.info('\n2️⃣  Fetching nature footage...')
    nature_mgr = NatureAssetManager()
    nature_videos = nature_mgr.fetch_nature_videos('peaceful nature', count=8)

    if not nature_videos:
        logger.error('Failed to fetch nature videos')
        return None

    logger.info(f'   ✅ Fetched {len(nature_videos)} nature videos')

    # Step 3: Get music
    logger.info('\n3️⃣  Getting peaceful music...')
    music_mgr = MusicManager()
    music_file = music_mgr.get_peaceful_music(duration=duration, theme=theme)

    if music_file:
        logger.info(f'   ✅ Music: {os.path.basename(music_file)}')
    else:
        logger.warning('   ⚠️  No music - video will be silent')

    # Step 4: Assemble video
    logger.info('\n4️⃣  Assembling meditation video...')
    assembler = MeditationVideoAssembler()

    try:
        video_file = assembler.assemble_meditation_video(
            nature_videos=nature_videos,
            scriptures=scriptures,
            music_file=music_file,
            duration=duration
        )

        if not video_file or not os.path.exists(video_file):
            logger.error('Video assembly failed')
            return None

        file_size = os.path.getsize(video_file) / (1024 * 1024)
        logger.info(f'   ✅ Video created: {os.path.basename(video_file)} ({file_size:.1f} MB)')

    except Exception as e:
        logger.error(f'Error assembling video: {e}')
        import traceback
        traceback.print_exc()
        return None

    # Step 5: Generate SEO metadata
    logger.info('\n5️⃣  Generating YouTube metadata...')
    seo_gen = SEOGenerator()
    metadata = seo_gen.generate_meditation_metadata(theme)

    # Add music attribution to description
    metadata['description'] += '\n\n🎵 MUSIC:\nMusic by Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0\nhttp://creativecommons.org/licenses/by/4.0/'

    logger.info(f'   ✅ Title: {metadata["title"]}')
    logger.info(f'   ✅ Tags: {len(metadata["tags"])} tags')

    # Step 6: Upload to YouTube
    logger.info('\n6️⃣  Uploading to YouTube...')
    try:
        uploader = YouTubeUploader()

        upload_metadata = {
            'title': metadata['title'],
            'description': metadata['description'],
            'tags': metadata['tags'],
            'category_id': str(metadata.get('category', '22')),  # People & Blogs
            'privacy_status': 'public',
            'made_for_kids': False
        }

        result = uploader.upload_video(
            video_file=video_file,
            metadata=upload_metadata,
            account_number=1
        )

        logger.info(f'   ✅ Upload complete!')
        logger.info(f'   📺 Video ID: {result["video_id"]}')
        logger.info(f'   🔗 URL: {result["video_url"]}')

        # Success summary
        logger.info('\n' + '='*70)
        logger.info('✅ SUCCESS! MEDITATION VIDEO LIVE ON YOUTUBE')
        logger.info('='*70)
        logger.info(f'Title:    {result["title"]}')
        logger.info(f'URL:      {result["video_url"]}')
        logger.info(f'Duration: {duration}s ({duration/60:.1f} minutes)')
        logger.info(f'Size:     {file_size:.1f} MB')
        logger.info('='*70)

        return result

    except Exception as e:
        logger.error(f'Upload failed: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create and upload meditation video to YouTube')
    parser.add_argument('--theme', default='peace and rest', help='Meditation theme')
    parser.add_argument('--duration', type=int, default=300, help='Video duration in seconds')
    parser.add_argument('--verses', type=int, default=8, help='Number of scripture verses')

    args = parser.parse_args()

    result = create_and_upload_meditation_video(
        theme=args.theme,
        duration=args.duration,
        verse_count=args.verses
    )

    if result:
        print(f'\n✅ SUCCESS!')
        print(f'🔗 Watch here: {result["video_url"]}')
    else:
        print('\n❌ Failed to create/upload video')
        sys.exit(1)
