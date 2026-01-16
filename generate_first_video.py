"""
Generate and Upload First WiseVirgin Video Using BALANCED EVENT-EMOTION MATRIX

This script will:
1. Track trending events
2. Score opportunities
3. Check content balance
4. Select best opportunity
5. Generate video (3-minute test, then scale to 8hr)
6. Upload to WiseVirgin YouTube channel
7. Record in content balancer
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engines.opportunity.event_tracker import EventTracker
from engines.opportunity.balanced_scorer import BalancedScorer
from engines.opportunity.content_balancer import ContentBalancer
from engines.content.scripture_curator import ScriptureCurator
from engines.production.scripture_narrator import ScriptureNarrator
from engines.production.nature_asset_manager import NatureAssetManager
from engines.production.music_manager import MusicManager
from engines.production.meditation_video_assembler import MeditationVideoAssembler
from engines.publishing.youtube_uploader import YouTubeUploader
from utils.logging_utils import setup_logger, get_daily_log_file
import subprocess
from datetime import datetime

logger = setup_logger("first_video_generator", get_daily_log_file())

async def generate_and_upload_first_video():
    """
    Complete workflow: Event tracking → Scoring → Video generation → Upload
    """
    logger.info("="*80)
    logger.info("WISEVIRGIN FIRST VIDEO GENERATION - BALANCED EVENT-EMOTION MATRIX")
    logger.info("="*80)

    # Step 1: Initialize components
    logger.info("Step 1/8: Initializing components...")
    tracker = EventTracker()
    scorer = BalancedScorer()
    balancer = ContentBalancer()

    # Step 2: Track trending events
    logger.info("Step 2/8: Tracking trending events...")

    # Use predefined high-scoring opportunity for first video
    # Based on strategy session: AI Joblessness + Anxiety scored 93/100
    best_opportunity = {
        "event": "AI Joblessness",
        "emotion": "Anxiety",
        "content_type": "negative",
        "score": 93
    }

    logger.info(f"Selected opportunity: {best_opportunity['event']} + {best_opportunity['emotion']}")
    logger.info(f"Content type: {best_opportunity['content_type']}")
    logger.info(f"Score: {best_opportunity['score']}/100")

    # Step 3: Video generation settings
    logger.info("Step 3/8: Configuring video settings...")

    # DYNAMIC MODE: Duration will be calculated based on actual narration length
    # Start with 6 verses for test video
    verses_needed = 6

    logger.info(f"Verses to curate: {verses_needed}")
    logger.info("Video duration will be calculated dynamically based on narration length")

    output_dir = "output/first_video"
    os.makedirs(output_dir, exist_ok=True)

    # Step 4: Curate scriptures
    logger.info("Step 4/8: Curating Bible verses...")
    curator = ScriptureCurator()

    scriptures = curator.curate_scriptures_for_event(
        event=best_opportunity["event"],
        emotion=best_opportunity["emotion"],
        count=verses_needed,
        theology="bride_of_christ"
    )

    logger.info(f"Curated {len(scriptures)} verses")
    for i, verse in enumerate(scriptures[:3], 1):
        logger.info(f"  Verse {i}: {verse['reference']}")

    # Step 5: Generate DYNAMIC synchronized voiceover
    logger.info("Step 5/8: Generating DYNAMIC synchronized voiceover narration...")
    narrator = ScriptureNarrator()
    narration_file = os.path.join(output_dir, "narration.mp3")

    narration_result = await narrator.generate_scripture_narration_dynamic(
        scriptures=scriptures,
        voice="female",
        output_file=narration_file,
        delay_before_reading=3,  # Wait 3s after text appears
        pause_after_reading=7     # Wait 7s after voiceover finishes
    )

    # Extract results
    narration_file = narration_result['output_file']
    verse_timings = narration_result['timings']
    duration = narration_result['total_duration']

    logger.info(f"Voiceover complete: {narration_file}")
    logger.info(f"Calculated video duration: {duration:.1f}s ({duration/60:.1f} minutes)")

    # Step 6: Get nature background and music
    logger.info("Step 6/8: Preparing nature background and music...")

    nature_manager = NatureAssetManager()
    nature_videos = nature_manager.fetch_nature_videos(
        theme="peaceful ocean waves" if best_opportunity["content_type"] == "negative" else "sunrise",
        count=1
    )

    if not nature_videos:
        logger.error("No nature videos found")
        return None

    logger.info(f"Nature video: {nature_videos[0]}")

    music_manager = MusicManager()
    music_file = music_manager.get_peaceful_music(duration=duration, theme='peace')
    logger.info(f"Background music: {music_file}")

    # Mix narration with music and normalize to YouTube standard (-14 LUFS)
    logger.info("Mixing audio with YouTube standard loudness normalization...")
    mixed_audio = os.path.join(output_dir, "mixed_audio.mp3")

    mix_cmd = [
        "ffmpeg", "-y",
        "-i", narration_file,
        "-i", music_file,
        "-filter_complex",
        # Narration at 150%, music at 15%, then normalize to YouTube standard -14 LUFS
        f"[0:a]volume=1.5[narration];[1:a]volume=0.15,aloop=loop=-1:size=2e+09[music];[narration][music]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=11:TP=-1.5[audio]",
        "-map", "[audio]",
        "-t", str(duration),
        mixed_audio
    ]

    subprocess.run(mix_cmd, check=True)
    logger.info("Audio mixing complete with YouTube standard loudness (-14 LUFS)")

    # Step 7: Assemble video with DYNAMIC timings
    logger.info("Step 7/8: Assembling meditation video with dynamic timing...")

    assembler = MeditationVideoAssembler()

    # Note: assemble_meditation_video() creates its own output file with timestamp
    # We'll get the output file path after it completes
    output_video = assembler.assemble_meditation_video(
        nature_videos=nature_videos,
        scriptures=scriptures,
        music_file=mixed_audio,  # Use our mixed audio (narration + music)
        duration=duration,
        verse_timings=verse_timings  # Pass dynamic timings for text overlays
    )

    logger.info(f"Video assembly complete: {output_video}")

    # Step 8: Generate SEO metadata and upload to YouTube
    logger.info("Step 8/8: Uploading to WiseVirgin YouTube channel...")

    # Generate title and description
    title = f"Bible Verses for {best_opportunity['emotion']} in Face of {best_opportunity['event']} | Sleep Meditation"

    description = f"""Find peace and comfort through scripture as you face {best_opportunity['event']}.

This meditation features {verses_needed} carefully curated Bible verses addressing {best_opportunity['emotion']} in the context of {best_opportunity['event']}. Each verse is narrated with a gentle voice over calming nature visuals and peaceful music.

Perfect for:
✓ Sleep meditation
✓ Background prayer
✓ Anxiety relief
✓ Stress reduction
✓ Spiritual comfort

All verses speak to your situation through eternal biblical truth.

🎵 Music: Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0
http://creativecommons.org/licenses/by/4.0/

🙏 Subscribe for more Bible meditation videos

#BibleVerses #{best_opportunity['emotion']} #{best_opportunity['event'].replace(' ', '')} #Meditation #Sleep #ChristianMeditation #Prayer #Peace
"""

    tags = [
        "bible verses",
        f"bible verses for {best_opportunity['emotion'].lower()}",
        best_opportunity['emotion'].lower(),
        best_opportunity['event'].lower(),
        "meditation",
        "sleep meditation",
        "christian meditation",
        "scripture meditation",
        "prayer",
        "peace",
        "comfort"
    ]

    # Upload to YouTube (using production account 3)
    uploader = YouTubeUploader()
    uploader.authenticate(account_number=3)

    metadata = {
        "title": title,
        "description": description,
        "tags": tags,
        "category_id": "22",  # People & Blogs
        "privacy_status": "public"
    }

    result = uploader.upload_video(
        video_file=output_video,
        metadata=metadata,
        account_number=3
    )

    # Extract video_id from dict response
    video_id = result.get('video_id') if isinstance(result, dict) else result

    if video_id:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"✅ VIDEO UPLOADED SUCCESSFULLY: {video_url}")

        # Record in content balancer
        balancer.record_video(
            video_id=video_id,
            event=best_opportunity["event"],
            emotion=best_opportunity["emotion"],
            content_type=best_opportunity["content_type"],
            score=best_opportunity["score"]
        )

        logger.info("✅ Recorded in content balancer")

        return {
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "event": best_opportunity["event"],
            "emotion": best_opportunity["emotion"],
            "content_type": best_opportunity["content_type"],
            "score": best_opportunity["score"],
            "duration": duration,
            "verses_count": len(scriptures)
        }
    else:
        logger.error("Upload failed")
        return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("WISEVIRGIN - FIRST VIDEO GENERATION")
    print("Using BALANCED EVENT-EMOTION MATRIX System")
    print("="*80 + "\n")

    result = asyncio.run(generate_and_upload_first_video())

    if result:
        print("\n" + "="*80)
        print("✅ FIRST VIDEO GENERATION COMPLETE!")
        print("="*80)
        print(f"\nVideo URL: {result['video_url']}")
        print(f"Title: {result['title']}")
        print(f"Event: {result['event']}")
        print(f"Emotion: {result['emotion']}")
        print(f"Content Type: {result['content_type']}")
        print(f"Score: {result['score']}/100")
        print(f"Duration: {result['duration']}s")
        print(f"Verses: {result['verses_count']}")
        print("\n✅ Recorded in content balancer for future balance tracking")
    else:
        print("\n❌ Video generation failed. Check logs for details.")
