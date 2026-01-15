"""
ENGINE 2.2: Script Generator
Uses AI to generate YouTube scripts based on research
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from utils.free_llm_client import FreeLLMClient
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('script_generator', get_daily_log_file())

class ScriptGenerator:
    def __init__(self):
        self.llm = FreeLLMClient()
    
    def build_prompt(self, topic, research_data):
        """Build prompt for script generation"""
        
        # Extract key info from research
        best_practices = research_data.get('best_practices', {})
        top_videos = research_data.get('top_videos', [])
        key_points = research_data.get('key_points', [])
        
        # Build video titles from top performers
        top_titles = [v['title'] for v in top_videos[:3]]
        
        # Build key points summary
        points_summary = '\n'.join([f"- {kp['snippet'][:100]}" for kp in key_points[:3]])
        
        prompt = f"""Write a YouTube video script for the topic: "{topic}"

TARGET AUDIENCE: Personal finance enthusiasts interested in AI tools

SCRIPT REQUIREMENTS:
- Length: 1,200-1,500 words (8-10 minutes spoken)
- Format: Faceless video (voiceover only, no on-camera presenter)
- Style: Informative, practical, engaging
- Tone: Friendly but professional

STRUCTURE (follow this exactly):
1. HOOK (0:00-0:15): Start with an attention-grabbing statement or question
2. PROBLEM (0:15-1:00): Explain the problem viewers face
3. SOLUTION OVERVIEW (1:00-2:00): Introduce the AI tool/method as solution
4. DETAILED TUTORIAL (2:00-7:00): Step-by-step guide with examples
5. TIPS & BEST PRACTICES (7:00-8:30): Pro tips and common mistakes
6. CALL TO ACTION (8:30-end): Ask for likes, subscribe, and tease next video

RETENTION HOOKS:
- Add a pattern interrupt or teaser every 60-90 seconds
- Examples: "But here's the crazy part...", "Wait until you see this...", "The real game-changer is..."

SUCCESSFUL EXAMPLES IN THIS NICHE:
{chr(10).join(top_titles)}

KEY POINTS TO COVER (from top videos):
{points_summary}

BEST PRACTICES:
{json.dumps(best_practices, indent=2)}

OUTPUT FORMAT:
- Write the full script as natural spoken language
- Include timestamps in [00:00] format
- Mark retention hooks with [HOOK]
- Keep sentences short and conversational
- Use transition words frequently

Generate the script now:"""
        
        return prompt
    
    def generate_script(self, topic, research_data):
        """Generate complete video script"""
        logger.info(f'Generating script for: {topic}')
        
        # Build prompt
        prompt = self.build_prompt(topic, research_data)
        
        # Generate with LLM
        try:
            script = self.llm.generate(prompt, max_tokens=2500, temperature=0.7)
            
            # Count words
            word_count = len(script.split())
            
            logger.info(f'Script generated: {word_count} words')
            
            return {
                'topic': topic,
                'script': script,
                'word_count': word_count,
                'estimated_duration': word_count / 150  # ~150 words per minute
            }
        
        except Exception as e:
            logger.error(f'Script generation failed: {e}')
            raise

if __name__ == '__main__':
    generator = ScriptGenerator()
    
    # Mock research data
    research_data = {
        'topic': 'ChatGPT for budgeting',
        'best_practices': {
            'script_structure': 'Hook -> Problem -> Solution -> CTA'
        },
        'top_videos': [
            {'title': 'How to Use ChatGPT for Your Budget'},
            {'title': 'AI Budgeting Made Easy'}
        ],
        'key_points': [
            {'snippet': 'ChatGPT can help you track expenses automatically'}
        ]
    }
    
    result = generator.generate_script('ChatGPT for budgeting', research_data)
    print(f"Word count: {result['word_count']}")
    print(f"Duration: {result['estimated_duration']:.1f} minutes")
    print(f"\nScript preview:\n{result['script'][:500]}...")
