"""
Meditation Video Assembler - Creates videos with scripture overlays and peaceful music
Supports multiple resolutions: 1920x1080 (16:9), 1080x1080 (1:1 square)
"""
import os
import subprocess
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap

from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('meditation_assembler', get_daily_log_file())

class MeditationVideoAssembler:
    def __init__(self):
        self.output_dir = 'output/videos'
        self.overlay_dir = 'output/overlays/scripture'
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.overlay_dir, exist_ok=True)

    def create_scripture_overlay(self, verse_text, reference, index, output_file=None, width=1920, height=1080):
        """
        Create a beautiful scripture overlay image with custom resolution

        Args:
            verse_text: Bible verse text
            reference: Bible reference (e.g., "John 3:16")
            index: Verse index
            output_file: Path to save overlay PNG
            width: Overlay width in pixels (default 1920)
            height: Overlay height in pixels (default 1080)
        """
        if not output_file:
            output_file = os.path.join(self.overlay_dir, f'scripture_{index}.png')

        # Create image with semi-transparent dark background
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calculate dimensions based on resolution
        scale_factor = min(width / 1920, height / 1080)

        # Add subtle dark overlay for text readability (proportional to height)
        overlay_top = int(height * 0.37)  # ~400px at 1080p
        overlay_bottom = int(height * 0.63)  # ~680px at 1080p
        overlay_box = [(0, overlay_top), (width, overlay_bottom)]
        draw.rectangle(overlay_box, fill=(0, 0, 0, 120))

        # Calculate font sizes
        verse_font_size = int(52 * scale_factor)
        ref_font_size = int(36 * scale_factor)

        # Try to load fonts
        try:
            verse_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', verse_font_size)
            ref_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', ref_font_size)
        except:
            try:
                verse_font = ImageFont.truetype('arial.ttf', verse_font_size)
                ref_font = ImageFont.truetype('arial.ttf', ref_font_size)
            except:
                verse_font = ImageFont.load_default()
                ref_font = ImageFont.load_default()

        # Clean verse text (remove quotes)
        clean_verse = verse_text.strip('"').strip("'")

        # Wrap text (proportional to width)
        wrap_width = int(50 * (width / 1920))
        wrapped = textwrap.fill(clean_verse, width=wrap_width)
        lines = wrapped.split('\n')

        # Draw verse text (centered)
        line_height = int(60 * scale_factor)
        y_position = int(height * 0.42)  # ~450px at 1080p

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=verse_font)
            text_width = bbox[2] - bbox[0]
            x_position = (width - text_width) // 2
            draw.text((x_position, y_position), line, fill=(255, 255, 255, 255), font=verse_font)
            y_position += line_height

        # Draw reference (centered below verse)
        y_position += int(20 * scale_factor)
        bbox = draw.textbbox((0, 0), reference, font=ref_font)
        ref_width = bbox[2] - bbox[0]
        x_position = (width - ref_width) // 2
        draw.text((x_position, y_position), reference, fill=(200, 200, 200, 255), font=ref_font)

        # Save
        img.save(output_file, 'PNG')
        logger.info(f'Created scripture overlay: {output_file} ({width}x{height})')
        return output_file

    def assemble_meditation_video(self, nature_videos, scriptures, music_file, duration=300, verse_timings=None, resolution="1920x1080"):
        """
        Assemble meditation video using ONE looped clip with text overlays

        Args:
            nature_videos: List of nature video paths
            scriptures: List of scripture dicts with 'verse' and 'reference'
            music_file: Path to background music
            duration: Video duration in seconds
            verse_timings: Optional dynamic timing data from narrator
            resolution: Video resolution (e.g., "1920x1080", "1080x1080")

        Returns:
            str: Path to output video
        """
        # Parse resolution
        width, height = resolution.split('x')
        width, height = int(width), int(height)

        logger.info(f'Assembling meditation video: {duration}s at {resolution} ({width}x{height})')

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_file = os.path.join(self.output_dir, f'{timestamp}_meditation_{resolution.replace("x", "_")}.mp4')

        # Create scripture overlays with custom resolution
        overlay_files = []
        for idx, verse_data in enumerate(scriptures):
            # Parse verse
            if isinstance(verse_data, str):
                if ' - ' in verse_data:
                    verse_text, reference = verse_data.rsplit(' - ', 1)
                else:
                    verse_text = verse_data
                    reference = ''
            else:
                # Support both 'verse' and 'text' keys
                verse_text = verse_data.get('verse', verse_data.get('text', ''))
                reference = verse_data.get('reference', '')

            overlay_file = os.path.join(self.overlay_dir, f'scripture_{idx}.png')
            self.create_scripture_overlay(verse_text, reference, idx, overlay_file, width, height)
            overlay_files.append(overlay_file)

        # Determine timing approach
        if verse_timings:
            logger.info(f'{len(scriptures)} verses with DYNAMIC timing')
        else:
            time_per_verse = duration / len(scriptures)
            logger.info(f'{len(scriptures)} verses, {time_per_verse:.1f}s per verse (fixed)')

        # Step 1: Loop single nature clip to fill exact duration
        base_video = os.path.join(self.output_dir, 'base_video.mp4')

        scale_cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1',  # Loop infinitely
            '-i', nature_videos[0],  # Use FIRST clip only
            '-t', str(duration),  # Stop at exact duration
            '-vf', f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-r', '25',
            '-an',  # No audio yet
            base_video
        ]

        subprocess.run(scale_cmd, check=True, capture_output=True)
        logger.info(f'Base video created: {resolution}')

        # Step 2: Build overlay filter for text overlays
        overlay_inputs = ['-i', base_video]
        for overlay_file in overlay_files:
            overlay_inputs.extend(['-i', overlay_file])

        overlay_filters = []
        current_time = 0

        for idx, overlay_file in enumerate(overlay_files):
            if verse_timings:
                # Use dynamic timing from narrator
                start_time = verse_timings[idx]['text_appears']
                if idx < len(verse_timings) - 1:
                    end_time = verse_timings[idx+1]['text_appears']
                else:
                    end_time = duration
            else:
                # Use fixed timing
                start_time = current_time
                time_per_verse = duration / len(scriptures)
                end_time = current_time + time_per_verse
                current_time = end_time

            if idx == 0:
                overlay_filters.append(
                    f"[0:v][{idx+1}:v]overlay=0:0:enable='between(t,{start_time},{end_time})'[v{idx}]"
                )
            else:
                overlay_filters.append(
                    f"[v{idx-1}][{idx+1}:v]overlay=0:0:enable='between(t,{start_time},{end_time})'[v{idx}]"
                )

        filter_complex = ';'.join(overlay_filters)

        # Step 3: Apply text overlays
        temp_video_with_text = os.path.join(self.output_dir, 'video_with_text.mp4')

        overlay_cmd = [
            'ffmpeg', '-y'
        ] + overlay_inputs + [
            '-filter_complex', filter_complex,
            '-map', f'[v{len(overlay_files)-1}]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-r', '25',
            '-t', str(duration),
            temp_video_with_text
        ]

        subprocess.run(overlay_cmd, check=True, capture_output=True)
        logger.info('Text overlays applied')

        # Step 4: Add audio
        audio_cmd = [
            'ffmpeg', '-y',
            '-i', temp_video_with_text,
            '-i', music_file,
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            output_file
        ]

        subprocess.run(audio_cmd, check=True, capture_output=True)
        logger.info(f'Final video created: {output_file}')

        # Cleanup
        if os.path.exists(base_video):
            os.remove(base_video)
        if os.path.exists(temp_video_with_text):
            os.remove(temp_video_with_text)

        return output_file
