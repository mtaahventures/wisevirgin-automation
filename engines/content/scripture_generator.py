"""
Scripture Generator - Creates scripture collections for meditation videos
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.free_llm_client import FreeLLMClient
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('scripture_generator', get_daily_log_file())

class ScriptureGenerator:
    def __init__(self):
        self.llm_client = FreeLLMClient()

    def generate_scripture_collection(self, theme='peace and rest', count=10):
        """Generate a collection of scripture verses for a theme"""
        logger.info(f'Generating {count} scripture verses for theme: {theme}')

        prompt = f'''You are a Bible scholar creating a peaceful meditation video.

Theme: {theme}

Generate exactly {count} Bible verses that relate to this theme.

CRITICAL FORMAT REQUIREMENTS:
1. Each verse MUST be on its own line
2. Format: "Verse text" - Book Chapter:Verse
3. Keep each verse under 150 characters for readability
4. Choose verses that are peaceful, contemplative, and uplifting
5. Use a mix of Old and New Testament
6. DO NOT add any extra text, explanations, or commentary
7. DO NOT number the verses

Example format:
"Be still, and know that I am God." - Psalm 46:10
"Come to me, all who are weary, and I will give you rest." - Matthew 11:28

Now generate {count} verses for the theme "{theme}":'''

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7,
                system_message='You are a Bible scholar creating peaceful meditation content. Generate scripture verses exactly as requested with proper formatting.'
            )

            # Parse verses
            verses = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and '-' in line:  # Valid verse format
                    verses.append(line)

            logger.info(f'Generated {len(verses)} scripture verses')

            return {
                'theme': theme,
                'verses': verses,
                'count': len(verses)
            }

        except Exception as e:
            logger.error(f'Error generating scriptures: {e}')
            # Fallback verses
            return {
                'theme': theme,
                'verses': [
                    '"Be still, and know that I am God." - Psalm 46:10',
                    '"The Lord is my shepherd; I shall not want." - Psalm 23:1',
                    '"Come to me, all who are weary, and I will give you rest." - Matthew 11:28',
                    '"Peace I leave with you; my peace I give you." - John 14:27',
                    '"The Lord bless you and keep you." - Numbers 6:24',
                    '"Be anxious for nothing, but in everything by prayer." - Philippians 4:6',
                    '"Cast all your anxiety on him because he cares for you." - 1 Peter 5:7',
                    '"The Lord is close to the brokenhearted." - Psalm 34:18',
                    '"He makes me lie down in green pastures." - Psalm 23:2',
                    '"I can do all things through Christ who strengthens me." - Philippians 4:13'
                ],
                'count': 10
            }

if __name__ == '__main__':
    gen = ScriptureGenerator()
    result = gen.generate_scripture_collection('peace and rest', 10)
    print(f"Generated {result['count']} verses:")
    for verse in result['verses']:
        print(f"  {verse}")
