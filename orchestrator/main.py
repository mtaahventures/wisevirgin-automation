#!/usr/bin/env python3
"""
WISEVIRGIN AUTOMATION - Master Orchestrator
Coordinates all 5 phases to create and publish YouTube videos automatically

Fully modular - each phase uses standalone engines
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Phase 1: Opportunity Intelligence
from engines.opportunity.topic_scorer import TopicScorer

# Phase 2: Content Generation
from engines.content.script_research import ScriptResearch
from engines.content.script_generator import ScriptGenerator
from engines.content.seo_generator import SEOGenerator

# Phase 3: Video Production
from engines.production.tts_engine import TTSEngine
from engines.production.asset_manager import AssetManager
from engines.production.video_assembler import VideoAssembler
from engines.production.text_overlay_generator import TextOverlayGenerator
from engines.production.visual_asset_generator import VisualAssetGenerator
from engines.production.thumbnail_gen import ThumbnailGenerator

# Phase 4: Publishing
from engines.publishing.youtube_uploader import YouTubeUploader
from engines.publishing.publish_tracker import PublishTracker

# Phase 5: Intelligence
from engines.intelligence.analytics import PerformanceAnalytics

from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('orchestrator', get_daily_log_file())

class SmartMoneyOrchestrator:
    def __init__(self):
        logger.info('='*60)
        logger.info('WISEVIRGIN AUTOMATION - Starting')
        logger.info('='*60)
        
        # Initialize all engines
        self.topic_scorer = TopicScorer()
        self.script_research = ScriptResearch()
        self.script_generator = ScriptGenerator()
        self.seo_generator = SEOGenerator()
        self.tts_engine = TTSEngine()
        self.asset_manager = AssetManager()
        self.video_assembler = VideoAssembler()
        self.text_overlay_gen = TextOverlayGenerator()
        self.visual_asset_gen = VisualAssetGenerator()
        self.thumbnail_gen = ThumbnailGenerator()
        self.youtube_uploader = YouTubeUploader()
        self.tracker = PublishTracker()
        self.analytics = PerformanceAnalytics()
    
    def run_full_pipeline(self):
        """Execute complete video creation & publishing pipeline"""
        try:
            logger.info('\n' + '='*60)
            logger.info('PHASE 1: OPPORTUNITY INTELLIGENCE')
            logger.info('='*60)
            
            # Find best topic
            opportunity = self.topic_scorer.find_best_topic()
            topic = opportunity['best_topic']['keyword']
            logger.info(f'Selected topic: {topic} (score: {opportunity["best_topic"]["total_score"]}/100)')
            
            logger.info('\n' + '='*60)
            logger.info('PHASE 2: CONTENT GENERATION')
            logger.info('='*60)
            
            # Research topic
            research = self.script_research.research_topic(topic)
            logger.info(f'Research complete: {research["video_count"]} videos analyzed')
            
            # Generate script
            timestamp = datetime.now().strftime('%Y-%m-%d')
            script_result = self.script_generator.generate_script(topic, research)
            script = script_result['script']
            word_count = script_result['word_count']
            logger.info(f'Script generated: {word_count} words ({script_result["estimated_duration"]:.1f} min)')
            
            # Save script for debugging
            os.makedirs('output/scripts', exist_ok=True)
            script_file = f'output/scripts/{timestamp}_script.txt'
            with open(script_file, 'w') as f:
                f.write(script)
            logger.info(f'Script saved: {script_file}')
            
            # Generate visual assets (slides, infographics, etc.)
            visual_cues = script_result.get('visual_cues', [])
            visual_assets = []
            if len(visual_cues) > 0:
                logger.info(f'Found {len(visual_cues)} visual cues in script')
                visual_assets = self.visual_asset_gen.generate_assets_from_visual_cues(visual_cues, script)
                logger.info(f'Generated {len(visual_assets)} visual assets')
            
            # Generate SEO metadata
            # Generate text overlays from script
            timestamp = datetime.now().strftime('%Y-%m-%d')
            overlays = self.text_overlay_gen.generate_overlays_from_script(script_result['script'], base_name=timestamp)
            logger.info(f'Generated {len(overlays)} text overlays')

            metadata = self.seo_generator.generate_metadata(topic, script_result)
            logger.info(f'SEO metadata: "{metadata["title"]}"')
            
            logger.info('\n' + '='*60)
            logger.info('PHASE 3: VIDEO PRODUCTION')
            logger.info('='*60)
            
            # Convert script to audio
            audio_result = self.tts_engine.text_to_speech(script)
            audio_file = audio_result['audio_file']
            logger.info(f'Voiceover created: {audio_result["duration"]:.1f}s')
            
            # Get stock footage
            stock_clips = self.asset_manager.get_assets_for_topic(topic, num_clips=15)
            logger.info(f'Stock footage downloaded: {len(stock_clips)} clips')
            
            # Assemble video
            # Assemble video with mixed visual assets
            if len(visual_assets) > 0:
                video_result = self.video_assembler.assemble_video_with_visual_assets(
                    audio_file, stock_clips, visual_assets
                )
                logger.info(f'Used {video_result.get("visual_assets_used", 0)} visual assets in video')
            else:
                video_result = self.video_assembler.assemble_video(audio_file, stock_clips)
            video_file = video_result['video_file']
            
            # Add text overlays to video
            if overlays and len(overlays) > 0:
                video_with_overlays = video_file.replace('_final.mp4', '_with_overlays.mp4')
                video_file = self.video_assembler.add_text_overlays_to_video(
                    video_file, overlays, video_with_overlays
                )
                logger.info(f'Text overlays composited onto video')

            logger.info(f'Video assembled: {video_file}')
            
            # Generate thumbnail
            thumbnail_file = self.thumbnail_gen.create_thumbnail(metadata['title'])
            logger.info(f'Thumbnail created: {thumbnail_file}')
            
            logger.info('\n' + '='*60)
            logger.info('PHASE 4: PUBLISHING')
            logger.info('='*60)
            
            # Upload to YouTube
            upload_result = self.youtube_uploader.upload_video(
                video_file,
                metadata,
                account_number=2
            )
            
            logger.info(f'Video uploaded: {upload_result["video_url"]}')
            
            # Set thumbnail
            self.youtube_uploader.set_thumbnail(
                upload_result['video_id'],
                thumbnail_file,
                account_number=2
            )
            
            # Track video
            self.tracker.track_video({
                'video_id': upload_result['video_id'],
                'video_url': upload_result['video_url'],
                'title': metadata['title'],
                'topic': topic,
                'video_file': video_file,
                'thumbnail_file': thumbnail_file,
                'metadata': metadata
            })
            
            logger.info('\n' + '='*60)
            logger.info('PHASE 5: ANALYTICS UPDATE')
            logger.info('='*60)
            
            # Update stats for all videos
            updated = self.analytics.update_all_videos()
            logger.info(f'Updated stats for {updated} videos')
            
            logger.info('\n' + '='*60)
            logger.info('SUCCESS - Video Published!')
            logger.info('='*60)
            logger.info(f'Video URL: {upload_result["video_url"]}')
            logger.info(f'Title: {metadata["title"]}')
            logger.info(f'Topic: {topic}')
            
            return {
                'success': True,
                'video_url': upload_result['video_url'],
                'video_id': upload_result['video_id'],
                'title': metadata['title']
            }
        
        except Exception as e:
            logger.error(f'Pipeline failed: {e}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

if __name__ == '__main__':
    orchestrator = SmartMoneyOrchestrator()
    result = orchestrator.run_full_pipeline()
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"Video published: {result['video_url']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")
        sys.exit(1)
