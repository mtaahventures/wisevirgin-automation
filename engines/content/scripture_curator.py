"""
Scripture Curator - Curates event-specific Bible verses using AI

Applies bride of Christ theological lens. Highly modular and reusable.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from groq import Groq
from utils.logging_utils import setup_logger, get_daily_log_file
import json
import time

logger = setup_logger("scripture_curator", get_daily_log_file())

class ScriptureCurator:
    def __init__(self, groq_api_key=None):
        """
        Initialize scripture curator with Groq API

        Args:
            groq_api_key: Groq API key for AI verse selection
        """
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")

        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY required for scripture curation")

        self.groq_client = Groq(api_key=self.groq_api_key)
        self.model = "llama-3.3-70b-versatile"

    def curate_scriptures_for_event(self, event, emotion, count=960, theology="bride_of_christ"):
        """
        Curate Bible verses specific to event + emotion combination

        Args:
            event: Event name (e.g., "AI Joblessness", "Wedding Day")
            emotion: Target emotion (e.g., "Anxiety", "Joy")
            count: Number of verses needed (default 960 for 8hr video)
            theology: Theological lens to apply (default "bride_of_christ")

        Returns:
            list: List of scripture objects [{"verse": "text", "reference": "Book Chapter:Verse"}]
        """
        try:
            logger.info(f"Curating {count} scriptures for: {event} + {emotion}")

            # Build prompt with theological lens
            if theology == "bride_of_christ":
                theological_context = """
                Apply the Bride of Christ theological lens:
                - Christ divorced the Law (first wife) by death
                - The Church is Christ's second wife/bride
                - The bride must die to the world to reunite with her post-resurrection husband
                - Speak to the viewer's situation through eternal biblical truth
                """
            else:
                theological_context = "Select verses that speak directly to the viewer's situation."

            prompt = f"""You are a biblical scholar curating scripture for meditation.

Event: {event}
Emotion: {emotion}
Theological Lens: {theology}

{theological_context}

Curate {count} Bible verses that:
1. Directly address the event "{event}" and emotion "{emotion}"
2. Are specific to this situation, not generic comfort verses
3. Provide hope, comfort, guidance, or peace
4. Range across Old and New Testament
5. Include both well-known and lesser-known verses
6. Apply the theological lens where appropriate

Return ONLY a JSON array of exactly {count} objects in this format:
[
  {{"verse": "Full verse text here", "reference": "Book Chapter:Verse"}},
  {{"verse": "Full verse text here", "reference": "Book Chapter:Verse"}}
]

IMPORTANT:
- Return ONLY the JSON array, no additional text
- Include exactly {count} verses
- Each verse must be unique
- Verse text should be complete and accurate (KJV or ESV preferred)
"""

            # For large counts, we'll request in batches and combine
            if count <= 50:
                # Single request for small counts
                verses = self._request_verses(prompt, count)
            else:
                # Batch requests for large counts
                verses = []
                batch_size = 50
                batches = (count + batch_size - 1) // batch_size

                for i in range(batches):
                    remaining = count - len(verses)
                    current_batch_size = min(batch_size, remaining)

                    batch_prompt = prompt.replace(f"{count} verses", f"{current_batch_size} verses")
                    batch_prompt = batch_prompt.replace(f"exactly {count} objects", f"exactly {current_batch_size} objects")

                    batch_verses = self._request_verses(batch_prompt, current_batch_size)

                    verses.extend(batch_verses)

                    logger.info(f"Batch {i+1}/{batches} complete: {len(verses)}/{count} verses")

                    # Rate limiting
                    if i < batches - 1:
                        time.sleep(2)

            # Ensure we have exactly the requested count
            if len(verses) < count:
                logger.warning(f"Only retrieved {len(verses)}/{count} verses, using fallback verses")
                verses = self._pad_with_fallback_verses(verses, count, event, emotion)
            elif len(verses) > count:
                verses = verses[:count]

            logger.info(f"Scripture curation complete: {len(verses)} verses")

            return verses

        except Exception as e:
            logger.error(f"Scripture curation error: {e}")
            # Return fallback verses
            return self._get_fallback_verses(count, event, emotion)

    def _request_verses(self, prompt, count):
        """
        Request verses from Groq API

        Args:
            prompt: Prompt text
            count: Expected number of verses

        Returns:
            list: List of verse objects
        """
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a biblical scholar providing scripture verses in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=8000
            )

            content = response.choices[0].message.content.strip()

            # Try to extract JSON array from response
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            verses = json.loads(content)

            # Validate structure
            if not isinstance(verses, list):
                raise ValueError("Response is not a JSON array")

            for verse in verses:
                if "verse" not in verse or "reference" not in verse:
                    raise ValueError("Invalid verse structure")

            return verses

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    def _pad_with_fallback_verses(self, verses, target_count, event, emotion):
        """
        Pad verses list with fallback verses to reach target count

        Args:
            verses: Current list of verses
            target_count: Target number of verses
            event: Event name
            emotion: Emotion

        Returns:
            list: Padded verses list
        """
        fallback_verses = self._get_fallback_verses(target_count - len(verses), event, emotion)
        verses.extend(fallback_verses)
        return verses

    def _get_fallback_verses(self, count, event, emotion):
        """
        Get fallback verses when API fails

        Args:
            count: Number of verses needed
            event: Event name
            emotion: Emotion

        Returns:
            list: Fallback verses
        """
        # Basic fallback verses that work for most situations
        fallback = [
            {"verse": "Be still, and know that I am God: I will be exalted among the heathen, I will be exalted in the earth.", "reference": "Psalm 46:10"},
            {"verse": "Come unto me, all ye that labour and are heavy laden, and I will give you rest.", "reference": "Matthew 11:28"},
            {"verse": "Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.", "reference": "John 14:27"},
            {"verse": "The Lord is my shepherd; I shall not want.", "reference": "Psalm 23:1"},
            {"verse": "Fear thou not; for I am with thee: be not dismayed; for I am thy God: I will strengthen thee; yea, I will help thee; yea, I will uphold thee with the right hand of my righteousness.", "reference": "Isaiah 41:10"},
            {"verse": "I can do all things through Christ which strengtheneth me.", "reference": "Philippians 4:13"},
            {"verse": "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.", "reference": "Romans 8:28"},
            {"verse": "Trust in the Lord with all thine heart; and lean not unto thine own understanding.", "reference": "Proverbs 3:5"},
            {"verse": "For I know the thoughts that I think toward you, saith the Lord, thoughts of peace, and not of evil, to give you an expected end.", "reference": "Jeremiah 29:11"},
            {"verse": "Cast thy burden upon the Lord, and he shall sustain thee: he shall never suffer the righteous to be moved.", "reference": "Psalm 55:22"}
        ]

        # Repeat fallback verses to reach target count
        result = []
        while len(result) < count:
            result.extend(fallback)

        return result[:count]

if __name__ == "__main__":
    # Test scripture curator
    curator = ScriptureCurator()

    # Test with small count
    verses = curator.curate_scriptures_for_event(
        event="AI Joblessness",
        emotion="Anxiety",
        count=10,
        theology="bride_of_christ"
    )

    print(f"Curated {len(verses)} verses:")
    for i, verse in enumerate(verses[:3], 1):
        print(f"{i}. {verse['reference']}: {verse['verse'][:80]}...")
