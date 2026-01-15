"""
ENGINE 2.4: SEO Generator - Reference-Quality Descriptions
Generates optimized title, description with ChatGPT prompts, tags for YouTube
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('seo_generator', get_daily_log_file())

class SEOGenerator:
    def __init__(self):
        pass

    def generate_title(self, topic, keyword_data=None):
        """Generate click-optimized YouTube title"""

        # Clean topic
        topic = topic.strip()

        # If topic already looks like a good title, use it
        if '|' in topic or '(' in topic:
            return topic[:100]  # YouTube limit

        # Build optimized title
        if 'chatgpt' in topic.lower() or 'ai' in topic.lower():
            # AI-focused title
            if 'budget' in topic.lower():
                title = "ChatGPT for Budgeting: Save $500/Month (Tutorial)"
            elif 'invest' in topic.lower():
                title = "AI Investment Guide: ChatGPT for Smart Investing"
            elif 'finance' in topic.lower():
                title = "ChatGPT for Personal Finance (Complete Guide 2026)"
            else:
                title = f"{topic.title()} (Step-by-Step Tutorial)"
        else:
            # General finance title
            title = f"{topic.title()} (Complete Guide)"

        # Ensure under 100 chars
        return title[:100]

    def generate_description(self, topic, script_data=None, chatgpt_prompts=None):
        """Generate SEO-optimized description with ChatGPT prompts library"""

        # Extract prompts if provided in script_data
        if script_data and 'chatgpt_prompts' in script_data:
            chatgpt_prompts = script_data['chatgpt_prompts']
        elif chatgpt_prompts is None:
            chatgpt_prompts = []

        # Build prompt library section
        prompts_section = ""
        if chatgpt_prompts:
            prompts_section = "\n\n🤖 CHATGPT PROMPTS (Copy-Paste Ready):\n\n"
            for i, prompt in enumerate(chatgpt_prompts, 1):
                # Clean and format prompt
                clean_prompt = prompt.strip().replace('\n', ' ').replace('  ', ' ')
                prompts_section += f"Prompt #{i}:\n{clean_prompt}\n\n"

        description = f"""Learn {topic.lower()} with this complete reference guide!

This video gives you EXACT ChatGPT prompts you can copy and use today. Screenshot the prompts when they appear on screen, or copy them from this description.

📌 QUICK REFERENCE (Jump to These Sections):
0:30 - The Problem
1:30 - ChatGPT Prompt #1 (screenshot at 2:00)
3:00 - Step-by-Step Walkthrough
4:30 - ChatGPT Prompt #2 (screenshot at 4:45)
5:30 - ChatGPT Prompt #3 (screenshot at 5:45)
6:30 - Real Results & Examples
8:00 - Quick Recap{prompts_section}
💰 FREE RESOURCES:
• Google Sheets Budget Template (no email required)
• Full Prompt Library PDF
• Monthly Money Review Checklist

📊 WHAT YOU'LL LEARN:
✅ Exact ChatGPT prompts for budgeting
✅ Step-by-step implementation
✅ Common mistakes to avoid
✅ Real savings examples

Perfect for beginners - no technical knowledge needed!

#PersonalFinance #ChatGPT #AITools #Budgeting #SaveMoney #FinancialFreedom

---

💡 MORE AI FINANCE TUTORIALS:
Subscribe for weekly videos on using AI for personal finance!

⚠️ DISCLAIMER: Educational purposes only. Not financial advice. Consult a professional before making financial decisions.

Smart Money Club USA - AI-Powered Personal Finance
https://www.youtube.com/@smartmoneyclubusa"""

        return description

    def generate_tags(self, topic):
        """Generate SEO tags"""
        # Mix of broad and specific tags
        tags = [
            'personal finance',
            'ai tools',
            'chatgpt',
            'chatgpt tutorial',
            'budgeting',
            'finance tips',
            'money management',
            'ai budgeting',
            'financial planning',
            'smart money',
            'save money',
            'chatgpt prompts',
            'ai personal finance',
            'budget tutorial'
        ]

        # Add topic-specific tags
        topic_lower = topic.lower()
        if 'invest' in topic_lower:
            tags.extend(['investing', 'investment tips', 'ai investing'])
        if 'save' in topic_lower or 'saving' in topic_lower:
            tags.extend(['saving money', 'money saving tips'])

        # Remove duplicates, limit to 15 tags
        tags = list(dict.fromkeys(tags))[:15]

        return tags

    def generate_metadata(self, topic, script_data=None, keyword_data=None):
        """Generate complete YouTube metadata"""
        logger.info(f'Generating SEO metadata for: {topic}')

        # Extract ChatGPT prompts if available
        chatgpt_prompts = None
        if script_data and isinstance(script_data, dict):
            chatgpt_prompts = script_data.get('chatgpt_prompts', [])

        title = self.generate_title(topic, keyword_data)
        description = self.generate_description(topic, script_data, chatgpt_prompts)
        tags = self.generate_tags(topic)

        metadata = {
            'title': title,
            'description': description,
            'tags': tags,
            'category_id': '26',  # Howto & Style
            'privacy_status': 'public',
            'made_for_kids': False
        }

        logger.info(f'SEO metadata generated: title={title}, {len(chatgpt_prompts) if chatgpt_prompts else 0} prompts in description')

        return metadata

if __name__ == '__main__':
    generator = SEOGenerator()

    # Test with sample prompts
    test_prompts = [
        "Act as a personal finance analyst. Analyze my transactions and give me necessity scores.",
        "Compare my spending this month vs last month and create a dashboard."
    ]

    result = generator.generate_metadata(
        'ChatGPT for budgeting',
        script_data={'chatgpt_prompts': test_prompts}
    )

    import json
    print(json.dumps(result, indent=2))
