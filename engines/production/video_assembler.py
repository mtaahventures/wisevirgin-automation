"""
ENGINE 3.3: Video Assembler - Enhanced
Combines voiceover + stock footage + visual assets (slides, images, graphics) using FFmpeg
"""
import os
import sys
import subprocess
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datetime import datetime
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('video_assembler', get_daily_log_file())

class VideoAssembler:
    def __init__(self):
        self.temp_dir = 'output/cache/temp'
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_audio_duration(self, audio_file):
        """Get duration of audio file"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    def get_video_duration(self, video_file):
        """Get duration of video file"""
        return self.get_audio_duration(video_file)

    def image_to_video(self, image_file, duration, output_file):
        """Convert static image to video segment"""
        cmd = [
            'ffmpeg',
            '-y',
            '-loop', '1',
            '-i', image_file,
            '-c:v', 'libx264',
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
            '-b:v', '2M',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def create_video_segment(self, video_clip, start_time, duration, output_file):
        """Create a video segment from clip"""
        cmd = [
            'ffmpeg',
            '-y',
            '-ss', str(start_time),
            '-i', video_clip,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:v', '2M',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def concatenate_clips(self, clip_list, output_file):
        """Concatenate multiple video clips"""
        concat_file = os.path.join(self.temp_dir, 'concat_list.txt')

        with open(concat_file, 'w') as f:
            for clip in clip_list:
                f.write(f"file '{os.path.abspath(clip)}'\n")

        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def add_audio_to_video(self, video_file, audio_file, output_file):
        """Add audio track to video"""
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_file
        ]

        subprocess.run(cmd, capture_output=True)
        return output_file

    def assemble_video_with_visual_assets(self, audio_file, stock_clips, visual_assets=None, output_path='output/videos'):
        """Assemble video mixing stock footage with visual assets (slides, images, graphics)"""
        logger.info('Assembling video with visual assets...')

        audio_duration = self.get_audio_duration(audio_file)
        logger.info(f'Audio duration: {audio_duration:.1f}s')

        # Default clip duration
        avg_clip_duration = 5
        clips_needed = int(audio_duration / avg_clip_duration) + 1

        prepared_clips = []
        clip_index = 0
        visual_asset_index = 0

        # Mix strategy: Every 3rd or 4th clip, use a visual asset instead of stock footage
        for i in range(clips_needed):
            segment_file = os.path.join(self.temp_dir, f'segment_{i}.mp4')

            # Decide whether to use visual asset or stock footage
            use_visual_asset = (visual_assets and
                               len(visual_assets) > 0 and
                               (i % 4 == 0 or i % 7 == 2) and  # Every 4th and some others
                               visual_asset_index < len(visual_assets))

            try:
                if use_visual_asset:
                    # Use visual asset (slide, infographic, etc.)
                    asset = visual_assets[visual_asset_index]
                    logger.info(f'Using visual asset {visual_asset_index}: {asset["type"]}')

                    # Convert image to video (show for 4-6 seconds)
                    display_duration = 5
                    self.image_to_video(asset['file'], display_duration, segment_file)
                    visual_asset_index += 1
                else:
                    # Use stock video footage
                    stock_clip = stock_clips[clip_index % len(stock_clips)]
                    clip_duration = self.get_video_duration(stock_clip)
                    start_time = random.uniform(0, max(0, clip_duration - avg_clip_duration))

                    self.create_video_segment(
                        stock_clip,
                        start_time,
                        min(avg_clip_duration, clip_duration),
                        segment_file
                    )
                    clip_index += 1

                prepared_clips.append(segment_file)
            except Exception as e:
                logger.warning(f'Error processing segment {i}: {e}')
                continue

        logger.info(f'Prepared {len(prepared_clips)} video segments (stock + visual assets)')

        # Concatenate all clips
        temp_video = os.path.join(self.temp_dir, 'temp_visual.mp4')
        self.concatenate_clips(prepared_clips, temp_video)

        # Trim to exact audio duration
        trimmed_video = os.path.join(self.temp_dir, 'temp_trimmed.mp4')
        trim_cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-t', str(audio_duration),
            '-c:v', 'libx264',
            '-b:v', '2M',
            trimmed_video
        ]
        subprocess.run(trim_cmd, capture_output=True)
        logger.info(f'Trimmed video to {audio_duration:.1f}s')

        # Add audio
        timestamp = datetime.now().strftime('%Y-%m-%d')
        final_output = os.path.join(output_path, f'{timestamp}_final.mp4')
        os.makedirs(output_path, exist_ok=True)

        self.add_audio_to_video(trimmed_video, audio_file, final_output)

        logger.info(f'Video assembled: {final_output}')

        # Cleanup
        for clip in prepared_clips:
            try:
                os.remove(clip)
            except:
                pass

        return {
            'video_file': final_output,
            'duration': audio_duration,
            'clips_used': len(prepared_clips),
            'visual_assets_used': visual_asset_index
        }

    def assemble_video(self, audio_file, stock_clips, output_path='output/videos'):
        """Legacy method - calls enhanced version with no visual assets"""
        return self.assemble_video_with_visual_assets(audio_file, stock_clips, None, output_path)

    def add_text_overlays_to_video(self, video_file, overlays, output_file):
        """Add text overlay images to video at specific timestamps"""
        if not overlays or len(overlays) == 0:
            logger.info("No text overlays to add, skipping")
            return video_file

        logger.info(f"Adding {len(overlays)} text overlays to video...")

        overlay_inputs = []
        filter_complex_parts = []

        for i, overlay_data in enumerate(overlays):
            overlay_inputs.extend(['-i', overlay_data['file']])

            start_times = [120, 270, 330]
            start_time = start_times[i] if i < len(start_times) else 180 + (i * 60)
            end_time = start_time + overlay_data.get('duration', 8)

            input_idx = i + 1
            prev_label = '[0:v]' if i == 0 else f'[tmp{i}]'
            curr_label = f'[tmp{i+1}]' if i < len(overlays) - 1 else '[out]'

            filter_complex_parts.append(
                f"{prev_label}[{input_idx}:v]overlay=0:0:enable='between(t,{start_time},{end_time})'{curr_label}"
            )

        filter_complex = ';'.join(filter_complex_parts)

        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_file
        ] + overlay_inputs + [
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-map', '0:a',
            '-c:v', 'libx264',
            '-c:a', 'copy',
            '-b:v', '2M',
            output_file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg overlay failed: {result.stderr}")
            return video_file

        logger.info(f"Text overlays added successfully: {output_file}")
        return output_file

if __name__ == '__main__':
    assembler = VideoAssembler()
    print("Enhanced video assembler created successfully")
    print("Supports: stock footage + presentation slides + infographics + stock images")
