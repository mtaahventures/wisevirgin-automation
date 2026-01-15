"""
ENGINE 2.4: SEO Generator
Generates optimized title, description, tags for YouTube
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
        # Title formulas that work:
        # 1. How to [outcome] using [method] ([result/timeframe])
        # 2. [Tool/Method] for [outcome] (Tutorial)
        # 3. [Number] Ways to [outcome] with [method]
        
        # Clean topic
        topic = topic.strip()
        
        # If topic already looks like a good title, use it
        if '|' in topic or '(' in topic:
            return topic[:100]  # YouTube limit
        
        # Build optimized title
        if 'chatgpt' in topic.lower() or 'ai' in topic.lower():
            # AI-focused title
            if 'budget' in topic.lower():
                title = "ChatGPT for Budgeting: Save 00/Month (Tutorial)"
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
    
    def generate_description(self, topic, script_preview=None):
        """Generate SEO-optimized description"""
        
        description = f"""Learn {topic.lower()} in this complete tutorial! 

In this video, I'll show you exactly how to use AI tools for personal finance, step-by-step.

📊 What You'll Learn:
• How to get started with AI for budgeting
• Best practices and tips
• Common mistakes to avoid
• Real examples you can use today

Perfect for beginners - no technical knowledge required!

⏰ Timestamps:
0:00 - Introduction
0:15 - The Problem
1:00 - The Solution
2:00 - Step-by-Step Tutorial
7:00 - Pro Tips
8:30 - Conclusion

🎯 Related Videos:
(AI will recommend related content)

💰 FREE Resources:
Check the description for links to the tools mentioned!

#PersonalFinance #AI #ChatGPT #Budgeting #FinanceTips

---

Smart Money Club USA - Your guide to AI-powered personal finance!

Subscribe for more AI finance tutorials: https://www.youtube.com/@smartmoneyclubusa

DISCLAIMER: This video is for educational purposes only. Not financial advice. Consult a professional before making financial decisions."""
        
        return description
    
    def generate_tags(self, topic):
        """Generate SEO tags"""
        # Mix of broad and specific tags
        tags = [
            'personal finance',
            'ai tools',
            'chatgpt',
            'budgeting',
            'finance tips',
            'money management',
            'ai budgeting',
            'financial planning',
            'smart money',
            'ai personal finance'
        ]
        
        # Add topic-specific tags
        topic_lower = topic.lower()
        if 'chatgpt' in topic_lower:
            tags.extend(['chatgpt tutorial', 'chatgpt finance', 'chatgpt budgeting'])
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
        
        title = self.generate_title(topic, keyword_data)
        description = self.generate_description(topic, script_data)
        tags = self.generate_tags(topic)
        
        metadata = {
            'title': title,
            'description': description,
            'tags': tags,
            'category_id': '26',  # Howto & Style (or '27' for Education)
            'privacy_status': 'public',
            'made_for_kids': False
        }
        
        logger.info(f'SEO metadata generated: title={title}')
        
        return metadata

if __name__ == '__main__':
    generator = SEOGenerator()
    result = generator.generate_metadata('ChatGPT for budgeting')
    
    import json
    print(json.dumps(result, indent=2))
