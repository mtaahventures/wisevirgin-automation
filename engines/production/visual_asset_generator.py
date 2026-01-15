"""
ENGINE 2.5: Visual Asset Generator
Generates presentation slides, infographics, AI images, and stock images for video
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('visual_asset_gen', get_daily_log_file())

class VisualAssetGenerator:
    def __init__(self):
        self.output_dir = 'output/visual_assets'
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f'{self.output_dir}/slides', exist_ok=True)
        os.makedirs(f'{self.output_dir}/graphics', exist_ok=True)
        os.makedirs(f'{self.output_dir}/stock_images', exist_ok=True)

    def generate_presentation_slide(self, text, title="", output_file=None):
        """Generate a PowerPoint-style presentation slide"""
        if output_file is None:
            output_file = os.path.join(f'{self.output_dir}/slides', f'slide_{hash(text) % 10000}.png')

        # Create 1920x1080 image (HD video resolution)
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='#1a1a2e')  # Dark blue background
        draw = ImageDraw.Draw(img)

        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Draw title if provided
        y_offset = 100
        if title:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((width - title_width) // 2, y_offset), title, fill='#00d4ff', font=title_font)
            y_offset += 180

        # Wrap and draw main text
        wrapped_lines = textwrap.wrap(text, width=50)
        line_height = 70

        for line in wrapped_lines[:10]:  # Max 10 lines
            text_bbox = draw.textbbox((0, 0), line, font=text_font)
            text_width = text_bbox[2] - text_bbox[0]
            draw.text(((width - text_width) // 2, y_offset), line, fill='#ffffff', font=text_font)
            y_offset += line_height

        # Add decorative elements
        draw.rectangle([100, height - 30, width - 100, height - 10], fill='#00d4ff')

        img.save(output_file)
        logger.info(f'Created presentation slide: {output_file}')
        return output_file

    def generate_infographic(self, title, items, output_file=None):
        """Generate an infographic with title and bullet points"""
        if output_file is None:
            output_file = os.path.join(f'{self.output_dir}/graphics', f'infographic_{hash(title) % 10000}.png')

        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='#0f3460')  # Dark background
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            item_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
        except:
            title_font = ImageFont.load_default()
            item_font = ImageFont.load_default()

        # Draw title
        y_offset = 80
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_offset), title, fill='#00d4ff', font=title_font)
        y_offset += 150

        # Draw items with bullet points
        for i, item in enumerate(items[:8]):  # Max 8 items
            # Draw bullet circle
            bullet_x = 200
            bullet_y = y_offset + 20
            draw.ellipse([bullet_x, bullet_y, bullet_x + 30, bullet_y + 30], fill='#16c79a')

            # Draw item text
            wrapped_item = textwrap.wrap(item, width=60)
            for line in wrapped_item:
                draw.text((bullet_x + 60, y_offset), line, fill='#ffffff', font=item_font)
                y_offset += 55
            y_offset += 20

        img.save(output_file)
        logger.info(f'Created infographic: {output_file}')
        return output_file

    def generate_calculation_graphic(self, calculations, total, output_file=None):
        """Generate a savings calculation graphic"""
        if output_file is None:
            output_file = os.path.join(f'{self.output_dir}/graphics', f'calculation_{hash(str(total)) % 10000}.png')

        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            calc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 55)
            total_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        except:
            title_font = ImageFont.load_default()
            calc_font = ImageFont.load_default()
            total_font = ImageFont.load_default()

        # Draw title
        title = "TOTAL SAVINGS"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, 100), title, fill='#00d4ff', font=title_font)

        # Draw calculations
        y_offset = 300
        for desc, amount in calculations:
            calc_text = f"{desc}: ${amount}/month"
            calc_bbox = draw.textbbox((0, 0), calc_text, font=calc_font)
            calc_width = calc_bbox[2] - calc_bbox[0]
            draw.text(((width - calc_width) // 2, y_offset), calc_text, fill='#ffffff', font=calc_font)
            y_offset += 80

        # Draw total with highlight
        total_text = f"TOTAL: ${total}/month"
        total_bbox = draw.textbbox((0, 0), total_text, font=total_font)
        total_width = total_bbox[2] - total_bbox[0]
        total_x = (width - total_width) // 2
        total_y = height - 250

        # Background rectangle for total
        draw.rectangle([total_x - 40, total_y - 20, total_x + total_width + 40, total_y + 100], fill='#16c79a')
        draw.text((total_x, total_y), total_text, fill='#1a1a2e', font=total_font)

        img.save(output_file)
        logger.info(f'Created calculation graphic: {output_file}')
        return output_file

    def download_stock_image(self, search_term, output_file=None):
        """Download a free stock image from Unsplash or Pexels"""
        if output_file is None:
            output_file = os.path.join(f'{self.output_dir}/stock_images', f'{search_term.replace(" ", "_")}.jpg')

        # Use Unsplash Source API (free, no API key needed)
        url = f"https://source.unsplash.com/1920x1080/?{search_term}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                logger.info(f'Downloaded stock image for "{search_term}": {output_file}')
                return output_file
            else:
                logger.warning(f'Failed to download stock image for "{search_term}"')
                return None
        except Exception as e:
            logger.error(f'Error downloading stock image: {e}')
            return None

    def generate_assets_from_visual_cues(self, visual_cues, script_content):
        """Generate all visual assets based on visual cues from script"""
        logger.info(f'Generating {len(visual_cues)} visual assets...')

        assets = []

        for cue in visual_cues:
            cue_type = cue['type']
            description = cue['description']

            try:
                if cue_type == 'presentation_slide':
                    # Extract prompt text from script if it's a prompt slide
                    if 'prompt' in description.lower():
                        # Look for nearby prompt in script
                        prompt_match = self._find_nearby_prompt(script_content, cue['index'])
                        if prompt_match:
                            asset_file = self.generate_presentation_slide(prompt_match, title="ChatGPT Prompt")
                            assets.append({'type': 'slide', 'file': asset_file, 'description': description})
                    else:
                        asset_file = self.generate_presentation_slide(description)
                        assets.append({'type': 'slide', 'file': asset_file, 'description': description})

                elif cue_type == 'infographic':
                    # Generate generic infographic
                    items = ["Tip 1: Track your expenses", "Tip 2: Cancel unused subscriptions", "Tip 3: Review monthly"]
                    asset_file = self.generate_infographic(description, items)
                    assets.append({'type': 'infographic', 'file': asset_file, 'description': description})

                elif cue_type == 'calculation_graphic':
                    # Generate calculation graphic
                    calcs = [("Netflix", 8), ("Starbucks", 120), ("Uber Eats", 95)]
                    asset_file = self.generate_calculation_graphic(calcs, 223)
                    assets.append({'type': 'calculation', 'file': asset_file, 'description': description})

                elif cue_type == 'stock_image':
                    # Download relevant stock image
                    search_term = self._extract_search_term(description)
                    asset_file = self.download_stock_image(search_term)
                    if asset_file:
                        assets.append({'type': 'stock_image', 'file': asset_file, 'description': description})

                else:
                    # Default: create a simple slide
                    asset_file = self.generate_presentation_slide(description)
                    assets.append({'type': 'slide', 'file': asset_file, 'description': description})

            except Exception as e:
                logger.error(f'Error generating asset for "{description}": {e}')
                continue

        logger.info(f'Generated {len(assets)} visual assets successfully')
        return assets

    def _find_nearby_prompt(self, script, cue_index):
        """Find ChatGPT prompt near a visual cue"""
        import re
        # Look for prompts in *'...'* format
        pattern = r"\*['\u2018\u2019](.+?)['\u2018\u2019]\*"
        matches = re.findall(pattern, script, re.DOTALL)

        if matches and cue_index < len(matches):
            return matches[cue_index]
        elif matches:
            return matches[0]
        return None

    def _extract_search_term(self, description):
        """Extract search term from visual cue description"""
        # Remove common words and extract key terms
        words = description.lower().split()
        keywords = [w for w in words if w not in ['show', 'display', 'a', 'the', 'with', 'and', 'or']]
        return ' '.join(keywords[:3]) if keywords else 'finance'


if __name__ == '__main__':
    generator = VisualAssetGenerator()

    # Test presentation slide
    slide = generator.generate_presentation_slide(
        "Act as a personal finance analyst. Analyze my spending.",
        title="ChatGPT Prompt #1"
    )
    print(f"Created slide: {slide}")

    # Test infographic
    infographic = generator.generate_infographic(
        "Common Mistakes",
        ["Don't paste 50+ transactions", "Only use posted transactions", "Implement ONE suggestion"]
    )
    print(f"Created infographic: {infographic}")

    # Test calculation
    calc = generator.generate_calculation_graphic(
        [("Netflix", 8), ("Starbucks", 120), ("Uber Eats", 95)],
        223
    )
    print(f"Created calculation: {calc}")
