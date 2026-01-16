"""
Scripture Narrator - Generates gentle TTS narration SYNCHRONIZED with text overlays
"""
import os
import sys
import asyncio
import edge_tts
import subprocess

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('scripture_narrator', get_daily_log_file())

class ScriptureNarrator:
    def __init__(self):
        self.output_dir = 'output/narration'
        os.makedirs(self.output_dir, exist_ok=True)

        # Calm, soothing voices for meditation
        self.voices = {
            'female': 'en-US-JennyNeural',  # Warm, gentle female voice
            'male': 'en-US-GuyNeural'       # Calm, soothing male voice
        }

    def _get_audio_duration(self, audio_file):
        """Get duration of audio file in seconds using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    async def generate_single_verse_narration(self, verse_text, reference, voice='female', output_file=None):
        """Generate TTS for a single verse"""
        voice_name = self.voices.get(voice, self.voices['female'])

        # Clean verse text
        clean_verse = verse_text.strip('"').strip("'")

        # Script: Read verse... pause... read reference... longer pause
        script = f'{clean_verse}... {reference}...... '

        if not output_file:
            output_file = os.path.join(self.output_dir, 'temp_verse.mp3')

        # Generate TTS (-40% slower for meditation)
        communicate = edge_tts.Communicate(script, voice_name, rate='-40%')
        await communicate.save(output_file)

        return output_file

    async def generate_scripture_narration_dynamic(self, scriptures, voice='female', output_file=None,
                                                   delay_before_reading=3, pause_after_reading=7):
        """
        Generate narration with DYNAMIC timing based on actual narration duration

        Timing logic:
        - Text overlay appears at calculated time
        - Voiceover starts 3 seconds after text appears
        - Voiceover reads the verse (measured duration)
        - Next text appears 7 seconds after voiceover finishes

        Args:
            scriptures: List of scripture dicts
            voice: 'female' or 'male'
            output_file: Output path
            delay_before_reading: Seconds to wait after text appears (default 3)
            pause_after_reading: Seconds to wait after voiceover finishes (default 7)

        Returns:
            dict: Contains output_file, timings array, and total_duration
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, 'scripture_narration.mp3')

        logger.info(f'Generating DYNAMIC narration: {len(scriptures)} verses')
        logger.info(f'  Delay before reading: {delay_before_reading}s')
        logger.info(f'  Pause after reading: {pause_after_reading}s')

        # Step 1: Generate all verse narrations and measure durations
        verse_narrations = []
        for idx, verse_data in enumerate(scriptures):
            # Parse verse
            if isinstance(verse_data, str):
                if ' - ' in verse_data:
                    verse_text, reference = verse_data.rsplit(' - ', 1)
                else:
                    verse_text = verse_data
                    reference = ''
            else:
                verse_text = verse_data.get('verse', verse_data.get('text', ''))
                reference = verse_data.get('reference', '')

            # Generate narration file
            verse_file = os.path.join(self.output_dir, f'verse_{idx}_narration.mp3')
            await self.generate_single_verse_narration(verse_text, reference, voice, verse_file)

            # Measure actual duration
            duration = self._get_audio_duration(verse_file)

            verse_narrations.append({
                'file': verse_file,
                'duration': duration,
                'verse_text': verse_text,
                'reference': reference
            })

            logger.info(f'Verse {idx+1} ({reference}): narration duration = {duration:.1f}s')

        # Step 2: Calculate dynamic timings
        timings = []
        current_time = 0

        for idx, verse_info in enumerate(verse_narrations):
            text_appears = current_time
            narration_starts = text_appears + delay_before_reading
            narration_ends = narration_starts + verse_info['duration']
            next_text_time = narration_ends + pause_after_reading

            timings.append({
                'index': idx,
                'text_appears': text_appears,
                'narration_starts': narration_starts,
                'narration_ends': narration_ends,
                'narration_duration': verse_info['duration'],
                'reference': verse_info['reference']
            })

            logger.info(f'Verse {idx+1} timing: text@{text_appears:.1f}s, voice@{narration_starts:.1f}s-{narration_ends:.1f}s')

            current_time = next_text_time

        # Total duration is when last narration ends + final pause
        total_duration = timings[-1]['narration_ends'] + pause_after_reading
        logger.info(f'Total video duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)')

        # Step 3: Create combined narration with silence base
        silence_file = os.path.join(self.output_dir, 'silence_base.mp3')
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-t', str(total_duration),
            '-c:a', 'libmp3lame',
            silence_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # Build FFmpeg filter to overlay each verse at narration_starts time
        filter_parts = []
        for idx, timing in enumerate(timings):
            delay_ms = int(timing['narration_starts'] * 1000)
            filter_parts.append(f"[{idx+1}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")

        # Mix all delayed verse audios
        mix_inputs = '[0:a]'
        for idx in range(len(timings)):
            mix_inputs += f'[a{idx}]'
        mix_filter = f"{mix_inputs}amix=inputs={len(timings)+1}:duration=first[out]"

        full_filter = ';'.join(filter_parts) + ';' + mix_filter if filter_parts else mix_filter

        # Build FFmpeg command
        inputs = ['-i', silence_file]
        for verse_info in verse_narrations:
            inputs.extend(['-i', verse_info['file']])

        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', full_filter,
            '-map', '[out]',
            '-c:a', 'libmp3lame',
            output_file
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # Cleanup temporary files
        os.remove(silence_file)
        for verse_info in verse_narrations:
            if os.path.exists(verse_info['file']):
                os.remove(verse_info['file'])

        logger.info(f'Dynamic narration complete: {output_file}')

        return {
            'output_file': output_file,
            'timings': timings,
            'total_duration': total_duration
        }

    async def generate_scripture_narration_synced(self, scriptures, duration, voice='female', output_file=None, delay_per_verse=3):
        """
        Generate narration SYNCHRONIZED with text overlay timing

        Creates separate narration for each verse, then uses FFmpeg to:
        1. Add silence before each verse's narration starts
        2. Position each narration at the correct timestamp

        Args:
            scriptures: List of scripture dicts
            duration: Total video duration
            voice: 'female' or 'male'
            output_file: Output path
            delay_per_verse: Seconds to wait after text appears before reading (default 3)
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, 'scripture_narration.mp3')

        logger.info(f'Generating SYNCHRONIZED narration: {len(scriptures)} verses, {duration}s total, {delay_per_verse}s delay per verse')

        # Calculate timing
        time_per_verse = duration / len(scriptures)

        # Generate individual verse narrations
        verse_audio_files = []
        for idx, verse_data in enumerate(scriptures):
            # Parse verse
            if isinstance(verse_data, str):
                if ' - ' in verse_data:
                    verse_text, reference = verse_data.rsplit(' - ', 1)
                else:
                    verse_text = verse_data
                    reference = ''
            else:
                verse_text = verse_data.get('verse', verse_data.get('text', ''))
                reference = verse_data.get('reference', '')

            # Generate this verse's narration
            verse_file = os.path.join(self.output_dir, f'verse_{idx}_narration.mp3')
            await self.generate_single_verse_narration(verse_text, reference, voice, verse_file)

            # Calculate when this verse's text appears
            verse_start_time = idx * time_per_verse
            # Narration should start AFTER the delay
            narration_start_time = verse_start_time + delay_per_verse

            verse_audio_files.append({
                'file': verse_file,
                'start_time': narration_start_time
            })

            logger.info(f'Verse {idx+1}: Text appears at {verse_start_time:.1f}s, narration starts at {narration_start_time:.1f}s')

        # Use FFmpeg to combine all verses with proper timing
        # Create a silent base audio of the full duration
        silence_file = os.path.join(self.output_dir, 'silence_base.mp3')
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-t', str(duration),
            '-c:a', 'libmp3lame',
            silence_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # Build FFmpeg filter to overlay each verse at the right time
        filter_parts = []
        for idx, verse_info in enumerate(verse_audio_files):
            # Delay this verse's audio to start at the correct time
            filter_parts.append(f"[{idx+1}:a]adelay={int(verse_info['start_time'] * 1000)}|{int(verse_info['start_time'] * 1000)}[a{idx}]")

        # Mix all delayed verse audios with the silence base
        mix_inputs = '[0:a]'
        for idx in range(len(verse_audio_files)):
            mix_inputs += f'[a{idx}]'

        mix_filter = f"{mix_inputs}amix=inputs={len(verse_audio_files)+1}:duration=first[out]"

        # Combine filters
        full_filter = ';'.join(filter_parts) + ';' + mix_filter if filter_parts else mix_filter

        # Build FFmpeg command
        input_params = ['-i', silence_file]
        for verse_info in verse_audio_files:
            input_params.extend(['-i', verse_info['file']])

        cmd = ['ffmpeg', '-y'] + input_params + [
            '-filter_complex', full_filter,
            '-map', '[out]',
            '-c:a', 'libmp3lame',
            '-t', str(duration),
            output_file
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # Cleanup temporary files
        os.remove(silence_file)
        for verse_info in verse_audio_files:
            if os.path.exists(verse_info['file']):
                os.remove(verse_info['file'])

        logger.info(f'SYNCHRONIZED scripture narration complete: {output_file}')
        return output_file

    def generate_narration_sync(self, scriptures, duration, voice='female', output_file=None, delay_per_verse=3):
        """Synchronous wrapper for async narration generation"""
        return asyncio.run(self.generate_scripture_narration_synced(scriptures, duration, voice, output_file, delay_per_verse))

if __name__ == '__main__':
    # Test
    narrator = ScriptureNarrator()
    test_scriptures = [
        {'text': 'Be still and know that I am God', 'reference': 'Psalm 46:10'},
        {'text': 'The Lord is my shepherd, I shall not want', 'reference': 'Psalm 23:1'}
    ]
    output = narrator.generate_narration_sync(test_scriptures, 60, voice='female', delay_per_verse=3)
    print(f'Synchronized narration created: {output}')
