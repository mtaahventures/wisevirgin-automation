"""
ENGINE 3.1: Text-to-Speech
Converts script to voiceover using free Edge-TTS
"""
import os
import sys
import asyncio
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import edge_tts
from utils.logging_utils import setup_logger, get_daily_log_file
from engines.content.script_cleaner import ScriptCleaner

logger = setup_logger('tts_engine', get_daily_log_file())

class TTSEngine:
    def __init__(self):
        self.script_cleaner = ScriptCleaner()
        # Best free voices for professional content
        self.voices = {
            'male_professional': 'en-US-GuyNeural',
            'female_professional': 'en-US-JennyNeural',
            'male_friendly': 'en-US-ChristopherNeural',
            'female_friendly': 'en-US-AriaNeural'
        }
        self.default_voice = self.voices['male_professional']

    async def generate_async(self, text, output_file, voice=None):
        """Generate TTS audio (async)"""
        if not voice:
            voice = self.default_voice

        logger.info(f'Generating TTS with voice: {voice}')

        # Create output directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Generate TTS
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        logger.info(f'TTS saved to: {output_file}')

        return output_file

    def generate(self, text, output_file, voice=None):
        """Generate TTS audio (sync wrapper)"""
        return asyncio.run(self.generate_async(text, output_file, voice))

    def text_to_speech(self, script, output_path='output/audio', voice_type='male_professional'):
        """Convert script to speech file"""
        logger.info('Converting script to speech...')

        # Clean script - remove production notes, visual cues, formatting
        clean_script = self.script_cleaner.clean_for_tts(script)
        logger.info(f'Cleaned script: {len(script)} -> {len(clean_script)} characters')

        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d')
        output_file = os.path.join(output_path, f'{timestamp}_voiceover.mp3')

        # Get voice
        voice = self.voices.get(voice_type, self.default_voice)

        # Generate TTS
        result_file = self.generate(clean_script, output_file, voice)

        # Get duration (approximate)
        word_count = len(clean_script.split())
        duration_seconds = (word_count / 150) * 60  # ~150 words per minute

        return {
            'audio_file': result_file,
            'duration': duration_seconds,
            'voice_used': voice
        }

if __name__ == '__main__':
    engine = TTSEngine()

    test_script = """
    Welcome to Smart Money Club USA! Today, I'll show you how to use ChatGPT for budgeting.
    If you're struggling to manage your finances, this tutorial will change everything.
    Let's dive in!
    """

    result = engine.text_to_speech(test_script)
    print(f"Audio generated: {result['audio_file']}")
    print(f"Duration: {result['duration']:.1f} seconds")
