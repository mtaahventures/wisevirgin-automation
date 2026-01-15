"""
Free LLM Client - Uses OpenAI free tier (gpt-4o-mini) with fallback
"""
import os
from openai import OpenAI

class FreeLLMClient:
    def __init__(self, api_key=None):
        # Try to get OpenAI key from environment
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = 'gpt-4o-mini'  # Cheapest model
        else:
            self.client = None
            self.model = None
    
    def generate(self, prompt, max_tokens=2000, temperature=0.7):
        """Generate text using free LLM"""
        if not self.client:
            raise Exception('No LLM client available. Set OPENAI_API_KEY environment variable.')
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a YouTube script writer specializing in Personal Finance and AI content. Write engaging, informative scripts optimized for watch time."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f'LLM generation error: {e}')
