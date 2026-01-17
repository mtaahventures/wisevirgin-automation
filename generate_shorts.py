"""
WiseVirgin Shorts Generator - Complete End-to-End System

Format: 1080x1080 (1:1 square)
Duration: 60 seconds
Verses: 2
Use Case: Cross-platform shorts, viral testing, event-emotion validation
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engines.opportunity.content_balancer import ContentBalancer
from engines.content.scripture_curator import ScriptureCurator
from engines.production.scripture_narrator import ScriptureNarrator
from engines.production.nature_asset_manager import NatureAssetManager
from engines.production.music_manager import MusicManager
from engines.production.meditation_video_assembler import MeditationVideoAssembler
from engines.publishing.round_robin_uploader import RoundRobinYouTubeUploader
from utils.logging_utils import setup_logger, get_daily_log_file
import subprocess
from datetime import datetime

logger = setup_logger("shorts_generator", get_daily_log_file())

# SHORTS CONFIGURATION
RESOLUTION = "1080x1080"
ASPECT_RATIO = "1:1"
DURATION_TARGET = 60  # seconds
VERSES_NEEDED = 2
DELAY_BEFORE_READING = 3
PAUSE_AFTER_READING = 5

async def generate_shorts_video(event, emotion, content_type, score=0):
    """
    Complete end-to-end shorts generation pipeline

    Args:
        event: Trending event
        emotion: Target emotion
        content_type: "positive" or "negative"
        score: Opportunity score (0-100)

    Returns:
        dict: Video details including video_id and URL
    """
    logger.info("="*80)
    logger.info("WISEVIRGIN SHORTS GENERATOR")
    logger.info(f"Event: {event} + Emotion: {emotion}")
    logger.info(f"Format: {RESOLUTION} ({ASPECT_RATIO}) | Duration: {DURATION_TARGET}s")
    logger.info("="*80)

    output_dir = f"output/shorts/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Curate scriptures
    logger.info(f"Step 1/7: Curating {VERSES_NEEDED} Bible verses...")
    curator = ScriptureCurator()

    scriptures = curator.curate_scriptures_for_event(
        event=event,
        emotion=emotion,
        count=VERSES_NEEDED,
        theology="bride_of_christ"
    )

    logger.info(f"Curated {len(scriptures)} verses")
    for i, verse in enumerate(scriptures, 1):
        logger.info(f"  Verse {i}: {verse['reference']}")

    # Step 2: Generate dynamic voiceover
    logger.info("Step 2/7: Generating voiceover narration...")
    narrator = ScriptureNarrator()
    narration_file = os.path.join(output_dir, "narration.mp3")

    narration_result = await narrator.generate_scripture_narration_dynamic(
        scriptures=scriptures,
        voice="female",
        output_file=narration_file,
        delay_before_reading=DELAY_BEFORE_READING,
        pause_after_reading=PAUSE_AFTER_READING
    )

    narration_file = narration_result['output_file']
    verse_timings = narration_result['timings']
    duration = narration_result['total_duration']

    logger.info(f"Voiceover complete: {duration:.1f}s")

    if duration > DURATION_TARGET:
        logger.warning(f"Duration {duration:.1f}s exceeds {DURATION_TARGET}s shorts limit")

    # Step 3: Get nature background
    logger.info("Step 3/7: Fetching nature background...")
    nature_manager = NatureAssetManager()
    nature_videos = nature_manager.fetch_nature_videos(
        theme="peaceful ocean waves" if content_type == "negative" else "sunrise",
        count=1
    )

    if not nature_videos:
        logger.error("No nature videos found")
        return None

    logger.info(f"Nature video: {nature_videos[0]}")

    # Step 4: Get background music
    logger.info("Step 4/7: Selecting background music...")
    music_manager = MusicManager()
    music_file = music_manager.get_peaceful_music(duration=duration, theme='peace')
    logger.info(f"Music: {music_file}")

    # Step 5: Mix audio (YouTube standard -14 LUFS)
    logger.info("Step 5/7: Mixing audio...")
    mixed_audio = os.path.join(output_dir, "mixed_audio.mp3")

    mix_cmd = [
        "ffmpeg", "-y",
        "-i", narration_file,
        "-i", music_file,
        "-filter_complex",
        f"[0:a]volume=1.5[narration];[1:a]volume=0.15,aloop=loop=-1:size=2e+09[music];[narration][music]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=11:TP=-1.5[audio]",
        "-map", "[audio]",
        "-t", str(duration),
        mixed_audio
    ]

    subprocess.run(mix_cmd, check=True)
    logger.info("Audio mixing complete")

    # Step 6: Assemble video (SQUARE FORMAT)
    logger.info(f"Step 6/7: Assembling video ({RESOLUTION})...")
    assembler = MeditationVideoAssembler()

    output_video = assembler.assemble_meditation_video(
        nature_videos=nature_videos,
        scriptures=scriptures,
        music_file=mixed_audio,
        duration=duration,
        verse_timings=verse_timings,
        resolution=RESOLUTION
    )

    logger.info(f"Video complete: {output_video}")

    # Step 7: Upload to YouTube
    logger.info("Step 7/7: Uploading to YouTube...")

    title = f"Bible Verses for {emotion} in Face of {event} | 60s Short"

    description = f"""Find peace through scripture for {event}.

{len(scriptures)} powerful Bible verses addressing {emotion} in the context of {event}.

Perfect for:
✓ Quick spiritual reset
✓ Faith encouragement
✓ Emotional support

🎵 Music: Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0

🙏 Subscribe for daily Bible Shorts

#BibleVerses #{emotion.replace(' ', '')} #{event.replace(' ', '')} #Shorts #ChristianShorts #Faith"""

    tags = [
        "bible verses",
        f"bible verses for {emotion.lower()}",
        emotion.lower(),
        event.lower(),
        "shorts",
        "youtube shorts",
        "christian shorts",
        "bible shorts",
        "faith",
        "prayer"
    ]

    uploader = RoundRobinYouTubeUploader()

    metadata = {
        "title": title,
        "description": description,
        "tags": tags,
        "category_id": "22",
        "privacy_status": "public"
    }

    video_id = uploader.upload_video(
        video_file=output_video,
        metadata=metadata
    )

    if video_id:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"✅ SHORTS UPLOADED: {video_url}")

        # Record in content balancer
        balancer = ContentBalancer()
        balancer.record_video(
            video_id=video_id,
            event=event,
            emotion=emotion,
            content_type=content_type,
            score=score
        )

        return {
            "video_id": video_id,
            "video_url": video_url,
            "title": title,
            "event": event,
            "emotion": emotion,
            "content_type": content_type,
            "score": score,
            "duration": duration,
            "verses_count": len(scriptures),
            "format": "shorts",
            "resolution": RESOLUTION
        }
    else:
        logger.error("Upload failed")
        return None

if __name__ == "__main__":
    print("\n" + "="*80)
    print("WISEVIRGIN SHORTS GENERATOR")
    print("60-Second Square Videos (1080x1080)")
    print("="*80 + "\n")

    # Default test
    event = "AI Joblessness"
    emotion = "Anxiety"
    content_type = "negative"
    score = 93

    result = asyncio.run(generate_shorts_video(event, emotion, content_type, score))

    if result:
        print("\n" + "="*80)
        print("✅ SHORTS GENERATION COMPLETE")
        print("="*80)
        print(f"\nVideo URL: {result['video_url']}")
        print(f"Title: {result['title']}")
        print(f"Duration: {result['duration']:.1f}s")
        print(f"Resolution: {result['resolution']}")
        print(f"Verses: {result['verses_count']}")
    else:
        print("\n❌ Generation failed. Check logs.")
