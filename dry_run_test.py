#!/usr/bin/env python3
"""
Dry run test - simulates full pipeline without actual video generation
Tests each phase with minimal API usage
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, '/root/smart-money-automation')

from utils.logging_utils import setup_logger

logger = setup_logger('dry_run')

def test_phase1():
    """Phase 1: Find best topic (minimal API calls)"""
    logger.info('=== PHASE 1: Opportunity Intelligence ===')

    from engines.opportunity.topic_scorer import TopicScorer

    scorer = TopicScorer()
    result = scorer.find_best_topic()

    if result and 'best_topic' in result:
        topic = result['best_topic']['keyword']
        score = result['best_topic'].get('total_score', result['best_topic'].get('score', 0))
        logger.info(f'✓ Best topic: {topic} (score: {score})')
        return topic
    else:
        logger.warning('No topic found, using hardcoded fallback')
        return 'ChatGPT for Personal Finance Automation'

def test_phase2(topic):
    """Phase 2: Generate content (uses OpenAI API)"""
    logger.info('=== PHASE 2: Content Generation ===')

    from engines.content.script_generator import ScriptGenerator
    from engines.content.seo_generator import SEOGenerator

    # Generate metadata (no API cost)
    seo_gen = SEOGenerator()
    metadata = seo_gen.generate_metadata(topic, {'word_count': 1500})
    logger.info(f'✓ Title: {metadata["title"]}')
    logger.info(f'✓ Description: {metadata["description"][:80]}...')
    logger.info(f'✓ Tags: {len(metadata["tags"])} tags')

    # Check if OpenAI key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key.startswith('YOUR') or len(api_key) < 20:
        logger.warning('⚠ OpenAI API key not properly configured - skipping script generation')
        logger.info('  (Script generation would cost ~$0.01 per video)')
        script = 'Demo script placeholder. OpenAI API key is required for real script generation.'
        return {'script': script, 'word_count': 100}, metadata

    logger.info('✓ OpenAI API key found - ready to generate scripts')
    # In dry run, don't actually call API
    logger.info('  (Skipping actual API call in dry run mode)')
    script = 'Demo script placeholder for dry run.'
    return {'script': script, 'word_count': 1500}, metadata

def test_phase3(script_result, metadata):
    """Phase 3: Video production (checks Pexels availability)"""
    logger.info('=== PHASE 3: Video Production ===')

    from engines.production.tts_engine import TTSEngine
    from engines.production.thumbnail_gen import ThumbnailGenerator
    from engines.production.asset_manager import AssetManager

    # Test TTS (free)
    logger.info('✓ TTS engine available (Microsoft Edge-TTS, 100% free)')

    # Test thumbnail (free)
    thumb_gen = ThumbnailGenerator()
    thumb_file = thumb_gen.create_thumbnail(metadata['title'])
    logger.info(f'✓ Thumbnail created: {thumb_file}')

    # Check Pexels API key
    pexels_key = os.getenv('PEXELS_API_KEY')
    if not pexels_key or pexels_key.startswith('YOUR') or len(pexels_key) < 20:
        logger.warning('✗ Pexels API key not configured!')
        logger.warning('  Cannot download stock footage without API key')
        logger.warning('  Get free key at: https://www.pexels.com/api/')
        logger.warning('  Then add to .env: PEXELS_API_KEY=your_key_here')
        return None

    # Test asset manager
    logger.info('✓ Pexels API key found - ready to download stock footage')
    logger.info('  (Would download 15-20 video clips here)')
    logger.info('  (Would assemble final video with FFmpeg here)')

    return thumb_file

def test_phase4():
    """Phase 4: Publishing (checks YouTube credentials)"""
    logger.info('=== PHASE 4: Publishing & Distribution ===')

    from engines.publishing.youtube_uploader import YouTubeUploader
    from engines.publishing.schedule_optimizer import ScheduleOptimizer
    from engines.publishing.publish_tracker import PublishTracker

    # Check YouTube credentials
    import os.path
    cred_file = '/root/youtube_tokens/credentials_1_token.pickle'
    if not os.path.exists(cred_file):
        logger.warning('✗ YouTube credentials not found!')
        logger.warning(f'  Expected: {cred_file}')
        return False

    logger.info(f'✓ YouTube credentials found: {cred_file}')

    # Test tracker (free)
    tracker = PublishTracker()
    videos = tracker.get_all_videos()
    logger.info(f'✓ Database initialized ({len(videos)} videos tracked)')

    # Test scheduler (free)
    scheduler = ScheduleOptimizer()
    next_time = scheduler.get_optimal_publish_time()
    logger.info(f'✓ Optimal publish time: {next_time}')

    logger.info('  (Would upload video to YouTube here)')
    return True

def main():
    logger.info('='*60)
    logger.info('SMART MONEY AUTOMATION - DRY RUN TEST')
    logger.info('Simulates full pipeline without API calls')
    logger.info('='*60)

    try:
        # Phase 1
        topic = test_phase1()

        # Phase 2
        script_result, metadata = test_phase2(topic)

        # Phase 3
        thumb_file = test_phase3(script_result, metadata)

        # Phase 4
        can_publish = test_phase4()

        # Summary
        logger.info('')
        logger.info('='*60)
        logger.info('DRY RUN SUMMARY')
        logger.info('='*60)

        openai_ok = os.getenv('OPENAI_API_KEY', '').strip() and not os.getenv('OPENAI_API_KEY').startswith('YOUR')
        pexels_ok = os.getenv('PEXELS_API_KEY', '').strip() and not os.getenv('PEXELS_API_KEY').startswith('YOUR')

        logger.info(f'1. Topic Selection:     ✓ (with fallback)')
        logger.info(f'2. Script Generation:   {"✓" if openai_ok else "✗"} OpenAI API key {"configured" if openai_ok else "NEEDED"}')
        logger.info(f'3. Video Production:    {"✓" if pexels_ok else "✗"} Pexels API key {"configured" if pexels_ok else "NEEDED"}')
        logger.info(f'4. YouTube Publishing:  {"✓" if can_publish else "✗"} Credentials {"found" if can_publish else "NEEDED"}')

        logger.info('='*60)

        ready = openai_ok and pexels_ok and can_publish

        if ready:
            logger.info('🎉 SYSTEM READY FOR PRODUCTION!')
            logger.info('')
            logger.info('To create first video:')
            logger.info('  cd /root/smart-money-automation')
            logger.info('  source venv/bin/activate')
            logger.info('  python3 orchestrator/main.py')
        else:
            logger.warning('')
            logger.warning('SETUP REQUIRED:')
            if not openai_ok:
                logger.warning('  1. OpenAI API key needed in .env')
                logger.warning('     Already configured in vault - see .env file')
            if not pexels_ok:
                logger.warning('  2. Pexels API key needed')
                logger.warning('     Get free at: https://www.pexels.com/api/')
                logger.warning('     Add to .env: PEXELS_API_KEY=your_key')
            if not can_publish:
                logger.warning('  3. YouTube credentials needed')
                logger.warning('     Check: /root/youtube_tokens/')

    except Exception as e:
        logger.error(f'Dry run failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
