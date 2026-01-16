"""
Long Form Generator - Generates 8-hour meditation videos

Integrates all components: event tracking, scoring, scripture curation, voiceover, video assembly.
Highly modular and reusable.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import asyncio
from utils.logging_utils import setup_logger, get_daily_log_file
from engines.content.scripture_curator import ScriptureCurator
from engines.production.scripture_narrator import ScriptureNarrator
from engines.production.meditation_video_assembler import MeditationVideoAssembler
from engines.production.nature_asset_manager import NatureAssetManager
from engines.production.music_manager import MusicManager
from engines.content.meditation_seo_generator import MeditationSEOGenerator

logger = setup_logger("long_form_generator", get_daily_log_file())

class LongFormGenerator:
    def __init__(self):
        """
        Initialize long-form video generator with all required components
        """
        self.duration_8hr = 28800  # 8 hours in seconds
        self.time_per_verse = 30  # 30 seconds per verse
        self.verses_needed = int(self.duration_8hr / self.time_per_verse)  # 960 verses

        logger.info(f"Long-form generator initialized: {self.verses_needed} verses for 8 hours")

    async def generate_8hour_video(self, event, emotion, content_type="negative", output_dir="output/longform"):
        """
        Generate complete 8-hour meditation video for specific event + emotion

        Args:
            event: Event name (e.g., "AI Joblessness")
            emotion: Target emotion (e.g., "Anxiety")
            content_type: "positive" or "negative"
            output_dir: Output directory for video files

        Returns:
            dict: Video metadata including file paths, title, description
        """
        try:
            logger.info(f"Starting 8-hour video generation: {event} + {emotion}")
            logger.info(f"Content type: {content_type}")

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Step 1: Curate scriptures
            logger.info(f"Step 1/6: Curating {self.verses_needed} scriptures...")
            curator = ScriptureCurator()
            scriptures = curator.curate_scriptures_for_event(
                event=event,
                emotion=emotion,
                count=self.verses_needed,
                theology="bride_of_christ"
            )

            logger.info(f"Scripture curation complete: {len(scriptures)} verses")

            # Step 2: Generate synchronized voiceover narration
            logger.info("Step 2/6: Generating synchronized voiceover narration...")
            narrator = ScriptureNarrator()
            narration_file = os.path.join(output_dir, "narration.mp3")

            await narrator.generate_scripture_narration_synced(
                scriptures=scriptures,
                duration=self.duration_8hr,
                voice="female",
                output_file=narration_file,
                delay_per_verse=3  # 3-second delay after text appears
            )

            logger.info(f"Voiceover narration complete: {narration_file}")

            # Step 3: Get nature video background
            logger.info("Step 3/6: Fetching nature video background...")
            nature_manager = NatureAssetManager()

            # Select nature theme based on emotion
            if content_type == "positive":
                nature_themes = ["sunrise", "beach", "flowers", "mountains"]
            else:
                nature_themes = ["rain", "ocean waves", "forest", "clouds"]

            nature_videos = nature_manager.fetch_nature_videos(
                query=nature_themes[0],
                count=1,
                min_duration=15
            )

            if not nature_videos:
                logger.warning("No nature videos found, using fallback")
                nature_videos = [os.path.join("output", "cache", "nature", "fallback.mp4")]

            logger.info(f"Nature background selected: {nature_videos[0]}")

            # Step 4: Get background music
            logger.info("Step 4/6: Selecting background music...")
            music_manager = MusicManager()
            music_file = music_manager.get_meditation_music()

            logger.info(f"Background music selected: {music_file}")

            # Step 5: Generate SEO metadata
            logger.info("Step 5/6: Generating SEO metadata...")
            seo_generator = MeditationSEOGenerator()

            # Create title with BALANCED MATRIX format
            title = f"Bible Verses for {emotion} in Face of {event} | 8 Hour Sleep Meditation"

            # Generate description
            description = f"""Find peace and comfort through scripture as you face {event}.

This 8-hour meditation features {self.verses_needed} carefully curated Bible verses addressing {emotion} in the context of {event}. Each verse is narrated with a gentle voice over calming nature visuals and peaceful music.

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

#BibleVerses #{emotion} #{event.replace(' ', '')} #Meditation #Sleep #ChristianMeditation #BibleStudy #Prayer #Peace #Comfort
"""

            tags = [
                "bible verses",
                f"bible verses for {emotion.lower()}",
                f"{emotion.lower()}",
                f"{event.lower()}",
                "meditation",
                "sleep meditation",
                "8 hour meditation",
                "christian meditation",
                "scripture meditation",
                "bible meditation",
                "prayer",
                "peace",
                "comfort",
                "relaxation",
                "stress relief"
            ]

            logger.info(f"SEO metadata complete: {title}")

            # Step 6: Assemble video
            logger.info("Step 6/6: Assembling 8-hour video...")
            assembler = MeditationVideoAssembler()

            output_video = os.path.join(output_dir, f"{event.replace(' ', '_')}_{emotion}_8hr.mp4")

            # Mix narration (70%) with music (30%)
            logger.info("Mixing narration with background music...")
            mixed_audio = os.path.join(output_dir, "mixed_audio.mp3")

            import subprocess
            mix_cmd = [
                "ffmpeg", "-y",
                "-i", narration_file,
                "-i", music_file,
                "-filter_complex",
                f"[0:a]volume=0.7[narration];[1:a]volume=0.3,aloop=loop=-1:size=2e+09[music];[narration][music]amix=inputs=2:duration=first[audio]",
                "-map", "[audio]",
                "-t", str(self.duration_8hr),
                mixed_audio
            ]

            subprocess.run(mix_cmd, check=True)
            logger.info("Audio mixing complete")

            # Assemble final video with looped background and scripture overlays
            logger.info("Assembling final video with text overlays...")

            # Create scripture overlays for each verse (every 30 seconds)
            # This will be integrated with existing meditation_video_assembler.py
            from engines.production.scripture_overlay_generator import ScriptureOverlayGenerator

            overlay_generator = ScriptureOverlayGenerator()
            overlay_files = []

            for idx, scripture in enumerate(scriptures):
                overlay_file = os.path.join(output_dir, "overlays", f"overlay_{idx}.png")
                os.makedirs(os.path.dirname(overlay_file), exist_ok=True)

                overlay_generator.create_scripture_overlay(
                    verse=scripture["verse"],
                    reference=scripture["reference"],
                    output_file=overlay_file
                )

                overlay_files.append(overlay_file)

                if (idx + 1) % 100 == 0:
                    logger.info(f"Generated {idx + 1}/{len(scriptures)} text overlays")

            logger.info(f"All {len(overlay_files)} text overlays generated")

            # Final video assembly
            assembler.assemble_meditation_video(
                nature_video=nature_videos[0],
                audio_file=mixed_audio,
                scriptures=scriptures,
                duration=self.duration_8hr,
                output_file=output_video
            )

            logger.info(f"8-hour video generation complete: {output_video}")

            # Return metadata
            metadata = {
                "video_file": output_video,
                "title": title,
                "description": description,
                "tags": tags,
                "duration": self.duration_8hr,
                "verses_count": len(scriptures),
                "event": event,
                "emotion": emotion,
                "content_type": content_type,
                "components": {
                    "narration": narration_file,
                    "music": music_file,
                    "nature_video": nature_videos[0],
                    "mixed_audio": mixed_audio,
                    "overlay_count": len(overlay_files)
                }
            }

            return metadata

        except Exception as e:
            logger.error(f"8-hour video generation error: {e}")
            raise

if __name__ == "__main__":
    # Test long-form generator
    async def test():
        generator = LongFormGenerator()

        # Generate test video (1 minute for testing, not 8 hours)
        generator.duration_8hr = 60  # 1 minute for testing
        generator.time_per_verse = 20  # 20 seconds per verse
        generator.verses_needed = 3  # 3 verses

        metadata = await generator.generate_8hour_video(
            event="AI Joblessness",
            emotion="Anxiety",
            content_type="negative",
            output_dir="output/test_longform"
        )

        print("Video generation complete:")
        print(f"Title: {metadata['title']}")
        print(f"File: {metadata['video_file']}")
        print(f"Verses: {metadata['verses_count']}")

    asyncio.run(test())
