"""
ENGINE 3.5: Text Overlay Generator
Creates screenshot-worthy text overlays for ChatGPT prompts and key information
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('text_overlay_gen', get_daily_log_file())

class TextOverlayGenerator:
    def __init__(self, output_dir='output/overlays'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Text overlay styling
        self.width = 1920
        self.height = 1080
        self.bg_color = (0, 0, 0, 200)  # Semi-transparent black
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 215, 0)  # Gold for important text
        self.border_color = (255, 215, 0)

    def extract_prompts_from_script(self, script):
        """Extract ChatGPT prompts from script"""
        prompts = []

        # Pattern 1: Prompts in quotes after action verbs
        pattern1 = r'["\'](Act as|You are|Create|Generate|Analyze|Help me|I need|Compare|Identify)[^"\']{30,}["\']'
        matches1 = re.findall(pattern1, script, re.IGNORECASE | re.DOTALL)

        for match in matches1:
            prompt_text = match.strip('"\'')
            if len(prompt_text) > 50 and len(prompt_text) < 500:
                prompts.append({
                    'type': 'chatgpt_prompt',
                    'text': prompt_text,
                    'title': 'PAUSE & COPY THIS CHATGPT PROMPT'
                })

        # Pattern 2: Look for "Step 1", "Step 2" checklists
        pattern2 = r'(Step \d+:[^\n]{20,150})'
        matches2 = re.findall(pattern2, script, re.IGNORECASE)

        if len(matches2) >= 3:
            steps_text = '\n'.join(matches2[:5])
            prompts.append({
                'type': 'checklist',
                'text': steps_text,
                'title': 'THE COMPLETE SYSTEM'
            })

        # Pattern 3: Look for numbered lists with savings/results
        pattern3 = r'(\d+\.[^\n]{30,120}[\$\d][^\n]{0,50})'
        matches3 = re.findall(pattern3, script)

        if len(matches3) >= 3:
            results_text = '\n'.join(matches3[:5])
            prompts.append({
                'type': 'results',
                'text': results_text,
                'title': 'SCREENSHOT THIS FOR REFERENCE'
            })

        logger.info(f'Extracted {len(prompts)} screenshot moments from script')
        return prompts

    def create_text_overlay(self, text, title, overlay_type='chatgpt_prompt', output_file=None):
        """Create a text overlay image"""

        # Create image with semi-transparent background
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Try to load a nice font, fallback to default
        try:
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 40)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Calculate centered box dimensions
        padding = 100
        box_width = self.width - (padding * 2)
        box_x = padding
        box_y = 150

        # Wrap text to fit width
        max_chars_per_line = 50
        wrapped_lines = []
        for line in text.split('\n'):
            wrapped = textwrap.fill(line, width=max_chars_per_line)
            wrapped_lines.extend(wrapped.split('\n'))

        # Calculate box height based on content
        line_height = 55
        box_height = len(wrapped_lines) * line_height + 250

        # Draw semi-transparent background box
        draw.rectangle(
            [(box_x, box_y), (box_x + box_width, box_y + box_height)],
            fill=self.bg_color
        )

        # Draw border
        border_width = 8
        draw.rectangle(
            [(box_x, box_y), (box_x + box_width, box_y + box_height)],
            outline=self.border_color,
            width=border_width
        )

        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        title_y = box_y + 30

        draw.text((title_x, title_y), title, fill=self.highlight_color, font=title_font)

        # Draw horizontal line under title
        line_y = title_y + 80
        draw.line(
            [(box_x + 50, line_y), (box_x + box_width - 50, line_y)],
            fill=self.highlight_color,
            width=3
        )

        # Draw wrapped text
        text_y = line_y + 40
        for line in wrapped_lines:
            draw.text((box_x + 60, text_y), line, fill=self.text_color, font=text_font)
            text_y += line_height

        # Save overlay
        if not output_file:
            timestamp = os.path.basename(output_file) if output_file else 'overlay'
            output_file = self.output_dir / f'{timestamp}_{overlay_type}.png'

        img.save(output_file, 'PNG')
        logger.info(f'Created text overlay: {output_file}')

        return str(output_file)

    def generate_overlays_from_script(self, script, base_name='overlay'):
        """Generate all text overlays from a script"""

        # Extract screenshot-worthy moments
        prompts = self.extract_prompts_from_script(script)

        overlays = []
        for i, prompt_data in enumerate(prompts):
            output_file = self.output_dir / f'{base_name}_{i+1}_{prompt_data["type"]}.png'

            overlay_path = self.create_text_overlay(
                text=prompt_data['text'],
                title=prompt_data['title'],
                overlay_type=prompt_data['type'],
                output_file=str(output_file)
            )

            overlays.append({
                'file': overlay_path,
                'type': prompt_data['type'],
                'text': prompt_data['text'],
                'duration': 8 if prompt_data['type'] == 'chatgpt_prompt' else 5
            })

        logger.info(f'Generated {len(overlays)} text overlays')
        return overlays

if __name__ == '__main__':
    generator = TextOverlayGenerator()

    # Test with sample prompt
    test_prompt = """Act as a personal finance analyst. I will paste my last 30 days of transactions.
For each expense, give me: 1) Necessity score 1-10, 2) Cheaper alternative, 3) Forgotten subscriptions.
Format as a table."""

    overlay = generator.create_text_overlay(
        test_prompt,
        'PAUSE & COPY THIS CHATGPT PROMPT',
        'test_prompt'
    )
    print(f'Test overlay created: {overlay}')
