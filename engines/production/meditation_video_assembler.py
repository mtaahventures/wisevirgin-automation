"""
Meditation Video Assembler - Creates videos with scripture overlays and peaceful music
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

    def create_scripture_overlay(self, verse_text, reference, index, output_file=None):
        """Create a beautiful scripture overlay image"""
        if not output_file:
            output_file = os.path.join(self.overlay_dir, f'scripture_{index}.png')

        # Create 1920x1080 image with semi-transparent dark background
        img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Add subtle dark overlay for text readability
        overlay_box = [(0, 400), (1920, 680)]
        draw.rectangle(overlay_box, fill=(0, 0, 0, 120))

        # Try to load fonts
        try:
            verse_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 52)
            ref_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf', 36)
        except:
            try:
                verse_font = ImageFont.truetype('arial.ttf', 52)
                ref_font = ImageFont.truetype('arial.ttf', 36)
            except:
                verse_font = ImageFont.load_default()
                ref_font = ImageFont.load_default()

        # Clean verse text (remove quotes)
        clean_verse = verse_text.strip('"').strip("'")

        # Wrap text
        wrapped = textwrap.fill(clean_verse, width=50)
        lines = wrapped.split('\n')

        # Draw verse text (centered)
        y_position = 450
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=verse_font)
            text_width = bbox[2] - bbox[0]
            x_position = (1920 - text_width) // 2
            draw.text((x_position, y_position), line, fill=(255, 255, 255, 255), font=verse_font)
            y_position += 60

        # Draw reference (centered below verse)
        y_position += 20
        bbox = draw.textbbox((0, 0), reference, font=ref_font)
        ref_width = bbox[2] - bbox[0]
        x_position = (1920 - ref_width) // 2
        draw.text((x_position, y_position), reference, fill=(200, 200, 200, 255), font=ref_font)

        # Save
        img.save(output_file, 'PNG')
        logger.info(f'Created scripture overlay: {output_file}')
        return output_file

    def assemble_meditation_video(self, nature_videos, scriptures, music_file, duration=300):
        """
        Assemble meditation video using ONE looped clip with text overlays

        SIMPLEST APPROACH:
        1. Take first nature clip and loop it to fill duration
        2. Add all text overlays on top
        3. Add music
        """
        logger.info(f'Assembling meditation video: {duration}s')

        timestamp = datetime.now().strftime('%Y-%m-%d')
        output_file = os.path.join(self.output_dir, f'{timestamp}_meditation.mp4')

        # Create scripture overlays
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
                verse_text = verse_data.get('text', '')
                reference = verse_data.get('reference', '')

            overlay_file = self.create_scripture_overlay(verse_text, reference, idx)
            overlay_files.append(overlay_file)

        # Calculate timing for text overlays
        time_per_verse = duration / len(scriptures)
        logger.info(f'{len(scriptures)} verses, {time_per_verse:.1f}s per verse')

        # STEP 1: Create continuous background from ONE nature clip
        logger.info('Creating continuous background from single nature clip...')

        # Use first nature video
        source_video = nature_videos[0]

        base_video = os.path.join(self.output_dir, f'{timestamp}_base.mp4')

        # Scale, loop, and trim to exact duration in one command
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1',  # Loop infinitely
            '-i', source_video,
            '-t', str(duration),  # Stop at exact duration
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-r', '25',  # Fixed 25fps
            '-an',  # No audio (will add music later)
            base_video
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f'Continuous background created from single clip ({duration}s)')

        # STEP 2: Add scripture overlays on top
        logger.info('Adding scripture overlays...')
        overlay_filters = []
        current_time = 0

        for idx, overlay_file in enumerate(overlay_files):
            start_time = current_time
            end_time = current_time + time_per_verse
            overlay_filters.append(
                f"[0:v][{idx+1}:v]overlay=0:0:enable='between(t,{start_time},{end_time})'[v{idx}]"
            )
            current_time = end_time

        # Build ffmpeg command with overlays
        input_params = ['-i', base_video]
        for overlay_file in overlay_files:
            input_params.extend(['-i', overlay_file])

        # Chain overlays
        if len(overlay_filters) == 1:
            filter_complex = overlay_filters[0]
            video_out = '[v0]'
        else:
            filter_complex = overlay_filters[0]
            for i in range(1, len(overlay_filters)):
                prev = f'[v{i-1}]'
                filter_complex += ';' + overlay_filters[i].replace('[0:v]', prev)
            video_out = f'[v{len(overlay_filters)-1}]'

        video_with_overlays = os.path.join(self.output_dir, f'{timestamp}_with_text.mp4')

        cmd = ['ffmpeg', '-y'] + input_params + [
            '-filter_complex', filter_complex,
            '-map', video_out,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            video_with_overlays
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info('Scripture overlays added')

        # STEP 3: Add background music
        if music_file and os.path.exists(music_file):
            logger.info('Adding peaceful music...')
            cmd = [
                'ffmpeg', '-y',
                '-i', video_with_overlays,
                '-i', music_file,
                '-filter_complex', f'[1:a]volume=0.3,aloop=loop=-1:size=2e+09[music];[music]atrim=0:{duration}[audio]',
                '-map', '0:v', '-map', '[audio]',
                '-c:v', 'copy', '-c:a', 'aac',
                '-shortest',
                output_file
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f'Music added: {output_file}')
        else:
            logger.warning('No music file - video will be silent')
            os.rename(video_with_overlays, output_file)

        # Cleanup
        if os.path.exists(base_video):
            os.remove(base_video)
        if os.path.exists(video_with_overlays) and os.path.exists(output_file):
            os.remove(video_with_overlays)

        logger.info(f'Meditation video complete: {output_file}')
        return output_file

if __name__ == '__main__':
    assembler = MeditationVideoAssembler()
    print('Meditation Video Assembler initialized')
