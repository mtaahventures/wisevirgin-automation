"""
ENGINE 2.2: Script Generator - Reference-Quality Content
Uses AI to generate bookmark-worthy YouTube scripts with copy-paste prompts
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import re
from utils.free_llm_client import FreeLLMClient
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('script_generator', get_daily_log_file())

class ScriptGenerator:
    def __init__(self):
        self.llm = FreeLLMClient()

    def build_prompt(self, topic, research_data):
        """Build prompt for reference-quality script generation"""

        top_videos = research_data.get('top_videos', [])
        key_points = research_data.get('key_points', [])

        top_titles = [v['title'] for v in top_videos[:3]]
        points_summary = '\n'.join([f"- {kp['snippet'][:100]}" for kp in key_points[:3]])

        prompt = """Write a YouTube video script for: "{}"

TARGET: Personal finance enthusiasts who want AI tools they can USE repeatedly

CRITICAL: Make this SO VALUABLE viewers screenshot it, bookmark it, and return multiple times.

SCRIPT STRUCTURE (1,000-1,200 words = 6:40-8:00 minutes at 150 words/min):

[HOOK - First 30 seconds] 75 words
Start with SPECIFIC result: "I saved $435 last month using this ChatGPT prompt..."
[VISUAL CUE: Show money savings graphic]

[PROBLEM - Next 60 seconds] 150 words
Real numbers and frustrations about manual expense tracking
[VISUAL CUE: Show stressed person with calculator]

[CHATGPT PROMPT #1 - Next 90 seconds] 250 words
Say: "Pause and copy this EXACT ChatGPT prompt word-for-word..."
[VISUAL CUE: Show prompt on presentation slide]

Then read the prompt SLOWLY inside asterisks and quotes:
*'Act as a personal finance analyst. I will paste my last 30 days of transactions.
For each expense, create a table with: 1) Date and merchant, 2) Category,
3) Necessity score 1-10, 4) Cheaper alternative, 5) Monthly savings potential.
After the table, identify three subscription services I might have forgotten about.'*

Explain why each part matters with specific examples.
[VISUAL CUE: Show ChatGPT interface screenshot]

[WALKTHROUGH - Next 90 seconds] 200 words
"Here is exactly how to use it:
Step 1: Export last 30 days from your bank as CSV
Step 2: Open ChatGPT, paste the prompt
Step 3: Paste your transactions below it
[VISUAL CUE: Show step-by-step tutorial slides]

Watch what happens... ChatGPT creates a table showing:
- Netflix: Score 7, Alternative: Family plan share, Saves $8/month
- Starbucks daily: Score 3, Alternative: Home brew, Saves $120/month
- Uber Eats: Score 2, Alternative: Meal prep, Saves $95/month

Total from these THREE examples: $223/month"
[VISUAL CUE: Show savings calculation with $8 + $120 + $95 = $223]

[CHATGPT PROMPT #2 - Next 60 seconds] 180 words
"Second prompt for finding forgotten subscriptions:
[VISUAL CUE: Show prompt on presentation slide]

*'Analyze these transactions. Identify: 1) All recurring charges, 2) Services
I am paying for multiple times, 3) Subscriptions used less than 3 times in
30 days, 4) Free alternatives. Format as cancellation priority list with savings.'*

Example findings:
- Gym membership unused 4 months: $49/month
- NYT subscription (duplicate with Apple News+): $17/month
Total from these TWO: $66/month"
[VISUAL CUE: Show subscription list]

[CHATGPT PROMPT #3 - Next 60 seconds] 180 words
"Final prompt - monthly review:
[VISUAL CUE: Show prompt on presentation slide]

*'Compare my spending this month vs last month. Create a dashboard:
1) Category changes with percent increase/decrease, 2) Largest single expense,
3) Days I spent over $100, 4) Trend: spending more or less?, 5) One action
to save $50+ next month.'*

Takes 30 seconds, complete financial review."
[VISUAL CUE: Show dashboard example]

[RESULTS & TIPS - Next 60 seconds] 200 words
"Three mistakes I made:
1. Don't paste 50+ transactions at once
2. Only export POSTED transactions
3. Implement ONE suggestion immediately
[VISUAL CUE: Show common mistakes infographic]

Pro tip: Run all three on the 1st of each month. Takes 12 minutes total."

[RECAP & CTA - Last 60 seconds] 165 words
"Recap the 3-Prompt Budget System:
Prompt 1: Expense Analyzer
Prompt 2: Subscription Hunter
Prompt 3: Monthly Review
[VISUAL CUE: Show system summary slide]

All prompts in description below. Free Google Sheets template included.

Subscribe for five ChatGPT prompts for analyzing stocks and ETFs.

Hit like if this helped. Comment your savings. Go run them now!"

CRITICAL MATH REQUIREMENTS:
✅ ALL savings numbers MUST add up correctly
✅ Use realistic examples: Netflix $8 + Starbucks $120 + Uber $95 = $223
✅ Don't claim higher savings than examples show
✅ Be conservative - underpromise, overdeliver

VISUAL CUE REQUIREMENTS:
✅ Mark key moments with [VISUAL CUE: description]
✅ Prompts on presentation slides
✅ Graphics for statistics

WRITING REQUIREMENTS:
✅ Specific numbers
✅ Read prompts SLOWLY inside *'...'* markers
✅ Explain WHY each part works
✅ Accurate math
✅ Name the system

❌ AVOID:
- Math that doesn't add up
- Timestamps (auto-calculated)
- Screenshot time references
- Generic advice

SUCCESSFUL EXAMPLES: {}
KEY INSIGHTS: {}

Generate complete script now. ENSURE ALL MATH IS ACCURATE.""".format(
            topic,
            chr(10).join(top_titles) if top_titles else 'N/A',
            points_summary if points_summary else 'N/A'
        )

        return prompt

    def generate_script(self, topic, research_data):
        """Generate reference-quality video script"""
        logger.info(f'Generating reference-quality script for: {topic}')

        prompt = self.build_prompt(topic, research_data)

        try:
            script = self.llm.generate(prompt, max_tokens=2500, temperature=0.7)
            word_count = len(script.split())
            chatgpt_prompts = self.extract_prompts(script)
            visual_cues = self.extract_visual_cues(script)

            logger.info(f'Script generated: {word_count} words, {len(chatgpt_prompts)} ChatGPT prompts, {len(visual_cues)} visual cues')

            return {
                'topic': topic,
                'script': script,
                'word_count': word_count,
                'estimated_duration': word_count / 150,
                'chatgpt_prompts': chatgpt_prompts,
                'visual_cues': visual_cues
            }
        except Exception as e:
            logger.error(f'Script generation failed: {e}')
            raise

    def extract_prompts(self, script):
        """Extract ChatGPT prompts from script for video description"""
        prompts = []

        pattern1 = r"\*['\u2018\u2019](.+?)['\u2018\u2019]\*"
        matches1 = re.findall(pattern1, script, re.DOTALL)

        for match in matches1:
            prompt_text = match.strip()
            starters = ['Act as', 'You are', 'Create', 'Generate', 'Analyze', 'Help me', 'I need', 'Compare', 'Identify']
            if any(prompt_text.startswith(s) for s in starters) and len(prompt_text) > 50:
                if prompt_text not in prompts:
                    prompts.append(prompt_text)

        return prompts[:5]

    def extract_visual_cues(self, script):
        """Extract visual cue markers from script"""
        visual_cues = []
        pattern = r'\[VISUAL CUE:\s*([^\]]+)\]'
        matches = re.findall(pattern, script, re.IGNORECASE)

        for i, match in enumerate(matches):
            visual_cues.append({
                'index': i,
                'description': match.strip(),
                'type': self._classify_visual_type(match)
            })

        return visual_cues

    def _classify_visual_type(self, description):
        """Classify visual cue into type"""
        desc_lower = description.lower()

        if 'slide' in desc_lower or 'presentation' in desc_lower or 'prompt' in desc_lower:
            return 'presentation_slide'
        elif 'graphic' in desc_lower or 'infographic' in desc_lower:
            return 'infographic'
        elif 'screenshot' in desc_lower or 'interface' in desc_lower:
            return 'screenshot'
        elif 'chart' in desc_lower or 'graph' in desc_lower or 'dashboard' in desc_lower:
            return 'chart'
        elif 'calculation' in desc_lower or 'savings' in desc_lower:
            return 'calculation_graphic'
        else:
            return 'stock_image'
