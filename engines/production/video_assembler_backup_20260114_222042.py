"""
ENGINE 3.3: Video Assembler
Combines voiceover + stock footage using FFmpeg (leverages existing patterns)
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
    
    def trim_video_clip(self, input_video, duration, output_file):
        """Trim video clip to specific duration"""
        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_video,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-c:a', 'aac',
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
        # Create concat file
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
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_file
        ]
        
        subprocess.run(cmd, capture_output=True)
        return output_file
    
    def assemble_video(self, audio_file, stock_clips, output_path='output/videos'):
        """Main method: Assemble final video from audio + stock footage"""
        logger.info('Assembling video...')
        
        # Get audio duration
        audio_duration = self.get_audio_duration(audio_file)
        logger.info(f'Audio duration: {audio_duration:.1f}s')
        
        # Calculate how many clips we need
        avg_clip_duration = 5  # Show each clip for 5 seconds
        clips_needed = int(audio_duration / avg_clip_duration) + 1
        
        # Prepare clips
        prepared_clips = []
        clip_index = 0
        
        for i in range(clips_needed):
            # Cycle through available stock clips
            stock_clip = stock_clips[clip_index % len(stock_clips)]
            clip_index += 1
            
            # Create trimmed segment
            segment_file = os.path.join(self.temp_dir, f'segment_{i}.mp4')
            
            try:
                clip_duration = self.get_video_duration(stock_clip)
                # Use random start point in clip
                start_time = random.uniform(0, max(0, clip_duration - avg_clip_duration))
                
                self.create_video_segment(
                    stock_clip,
                    start_time,
                    min(avg_clip_duration, clip_duration),
                    segment_file
                )
                
                prepared_clips.append(segment_file)
            except Exception as e:
                logger.warning(f'Error processing clip {i}: {e}')
                continue
        
        logger.info(f'Prepared {len(prepared_clips)} video segments')
        
        # Concatenate all clips
        temp_video = os.path.join(self.temp_dir, 'temp_visual.mp4')
        self.concatenate_clips(prepared_clips, temp_video)
        
        # Add audio to video
        timestamp = datetime.now().strftime('%Y-%m-%d')
        final_output = os.path.join(output_path, f'{timestamp}_final.mp4')
        os.makedirs(output_path, exist_ok=True)
        
        self.add_audio_to_video(temp_video, audio_file, final_output)
        
        logger.info(f'Video assembled: {final_output}')
        
        # Cleanup temp files
        for clip in prepared_clips:
            try:
                os.remove(clip)
            except:
                pass
        
        return {
            'video_file': final_output,
            'duration': audio_duration,
            'clips_used': len(prepared_clips)
        }


    def add_text_overlays_to_video(self, video_file, overlays, output_file):
        """Add text overlay images to video at specific timestamps using FFmpeg"""
        if not overlays or len(overlays) == 0:
            logger.info("No text overlays to add, skipping")
            return video_file

        logger.info(f"Adding {len(overlays)} text overlays to video...")

        # Build FFmpeg overlay filter
        # Format: overlay=x=0:y=0:enable='between(t,START,END)'
        overlay_inputs = []
        filter_complex_parts = []

        for i, overlay_data in enumerate(overlays):
            overlay_inputs.extend(['-i', overlay_data['file']])

            # Calculate when to show this overlay
            # Show prompts at 2min, 4:30min, 5:30min marks
            start_times = [120, 270, 330]  # 2:00, 4:30, 5:30
            start_time = start_times[i] if i < len(start_times) else 180 + (i * 60)
            end_time = start_time + overlay_data.get('duration', 8)

            # Build overlay filter
            input_idx = i + 1  # Input 0 is video, 1+ are overlays
            prev_label = 'v' if i == 0 else f'tmp{i}'
            curr_label = f'tmp{i+1}' if i < len(overlays) - 1 else 'out'

            filter_complex_parts.append(
                f'{prev_label}[{input_idx}:v]overlay=0:0:enable='"'"'between(t,{start_time},{end_time})'"'"'[{curr_label}]'
            )

        filter_complex = ';'.join(filter_complex_parts)

        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_file
        ] + overlay_inputs + [
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-map', '0:a',  # Keep original audio
            '-c:v', 'libx264',
            '-c:a', 'copy',
            '-b:v', '2M',
            output_file
        ]

        logger.info(f"Running FFmpeg overlay command...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg overlay failed: {result.stderr}")
            return video_file  # Return original if overlay fails

        logger.info(f"Text overlays added successfully: {output_file}")
        return output_file

if __name__ == '__main__':
    assembler = VideoAssembler()
    
    # Test with mock data
    print("Video assembler engine created successfully")
    print("Requires: audio file + list of stock clips")

