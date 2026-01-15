#!/usr/bin/env python3
"""
Quick system test script - tests each phase without full execution
"""
import os
import sys

# Add project root to path
sys.path.insert(0, '/root/smart-money-automation')

from utils.logging_utils import setup_logger

logger = setup_logger('test_system')

def test_phase1_opportunity():
    """Test Phase 1: Opportunity Intelligence"""
    logger.info("Testing Phase 1: Opportunity Intelligence...")
    try:
        from engines.opportunity.trend_monitor import TrendMonitor
        from engines.opportunity.keyword_research import KeywordResearch
        from engines.opportunity.topic_scorer import TopicScorer
        
        # Test trend monitor (no API key needed for pytrends)
        trend_monitor = TrendMonitor()
        trends = trend_monitor.get_google_trends(['ai budgeting', 'chatgpt money'])
        logger.info(f"✓ Trend Monitor: Found {len(trends)} trends")
        
        # Test keyword research
        keyword_research = KeywordResearch()
        suggestions = keyword_research.get_youtube_autocomplete('ai for personal finance')
        logger.info(f"✓ Keyword Research: Found {len(suggestions)} suggestions")
        
        # Test topic scorer
        topic_scorer = TopicScorer()
        logger.info("✓ Topic Scorer initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ Phase 1 failed: {e}")
        return False

def test_phase2_content():
    """Test Phase 2: Content Generation"""
    logger.info("Testing Phase 2: Content Generation...")
    try:
        from engines.content.script_research import ScriptResearch
        from engines.content.seo_generator import SEOGenerator
        
        # Test SEO generator (no API needed)
        seo_gen = SEOGenerator()
        metadata = seo_gen.generate_metadata('ChatGPT for Budget Planning', 
                                            {'word_count': 1500, 'duration_minutes': 10})
        logger.info(f"✓ SEO Generator: Generated title '{metadata['title'][:50]}...'")
        logger.info(f"  Tags: {len(metadata['tags'])} tags")
        
        # Test script research initialization
        script_research = ScriptResearch()
        logger.info("✓ Script Research initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ Phase 2 failed: {e}")
        return False

def test_phase3_production():
    """Test Phase 3: Video Production"""
    logger.info("Testing Phase 3: Video Production...")
    try:
        from engines.production.tts_engine import TTSEngine
        from engines.production.thumbnail_gen import ThumbnailGenerator
        
        # Test TTS engine initialization
        tts = TTSEngine()
        logger.info(f"✓ TTS Engine: {len(tts.voices)} voices available")
        
        # Test thumbnail generator
        thumb_gen = ThumbnailGenerator()
        test_dir = '/tmp'
        thumb_file = thumb_gen.create_thumbnail('Test Title: AI for Personal Finance', test_dir)
        if os.path.exists(thumb_file):
            size = os.path.getsize(thumb_file)
            logger.info(f"✓ Thumbnail Generator: Created {size} byte thumbnail")
            os.remove(thumb_file)
        
        return True
    except Exception as e:
        logger.error(f"✗ Phase 3 failed: {e}")
        return False

def test_phase4_publishing():
    """Test Phase 4: Publishing & Distribution"""
    logger.info("Testing Phase 4: Publishing & Distribution...")
    try:
        from engines.publishing.publish_tracker import PublishTracker
        from engines.publishing.schedule_optimizer import ScheduleOptimizer
        
        # Test tracker database
        tracker = PublishTracker()
        all_videos = tracker.get_all_videos()
        total_videos = len(all_videos)
        logger.info(f"✓ Publish Tracker: Database has {total_videos} videos")
        
        # Test schedule optimizer
        scheduler = ScheduleOptimizer()
        next_time = scheduler.get_optimal_publish_time()
        logger.info(f"✓ Schedule Optimizer: Next optimal time is {next_time}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Phase 4 failed: {e}")
        return False

def test_phase5_intelligence():
    """Test Phase 5: Intelligence & Learning"""
    logger.info("Testing Phase 5: Intelligence & Learning...")
    try:
        from engines.intelligence.pattern_detector import PatternDetector
        
        # Test pattern detector
        detector = PatternDetector()
        logger.info("✓ Pattern Detector initialized")
        
        return True
    except Exception as e:
        logger.error(f"✗ Phase 5 failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("Smart Money Automation - System Test")
    logger.info("="*60)
    
    results = {
        'Phase 1 - Opportunity Intelligence': test_phase1_opportunity(),
        'Phase 2 - Content Generation': test_phase2_content(),
        'Phase 3 - Video Production': test_phase3_production(),
        'Phase 4 - Publishing & Distribution': test_phase4_publishing(),
        'Phase 5 - Intelligence & Learning': test_phase5_intelligence(),
    }
    
    logger.info("="*60)
    logger.info("Test Results Summary:")
    logger.info("="*60)
    
    for phase, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status} - {phase}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    logger.info("="*60)
    logger.info(f"Overall: {total_passed}/{total_tests} phases passed")
    logger.info("="*60)
    
    if total_passed == total_tests:
        logger.info("All systems operational! Ready for production.")
        return 0
    else:
        logger.warning("Some systems failed. Check errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
