"""
ENGINE 3.4: Thumbnail Generator
Creates clickable thumbnails using Pillow (reusable for any project)
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger('thumbnail_gen', get_daily_log_file())

class ThumbnailGenerator:
    def __init__(self):
        self.width = 1280
        self.height = 720
        self.bg_color = (30, 30, 50)  # Dark blue
        self.accent_color = (0, 200, 100)  # Green (money)
    
    def create_thumbnail(self, title, output_path='output/thumbnails'):
        """Generate thumbnail for video"""
        logger.info('Generating thumbnail...')
        
        # Create image
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default
        try:
            # Try system fonts
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
            subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 40)
        except:
            # Fallback to default
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add title text (wrap if too long)
        max_width = self.width - 100
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=title_font)
                width = bbox[2] - bbox[0]
            except:
                width = len(test_line) * 40  # Rough estimate
            
            if width < max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw title lines
        y_offset = 200
        for line in lines[:3]:  # Max 3 lines
            # Draw shadow
            draw.text((52, y_offset + 2), line, fill=(0, 0, 0), font=title_font)
            # Draw text
            draw.text((50, y_offset), line, fill=(255, 255, 255), font=title_font)
            y_offset += 90
        
        # Add accent bar
        draw.rectangle([(50, 550), (1230, 570)], fill=self.accent_color)
        
        # Add subtitle
        subtitle = "Smart Money Club USA"
        draw.text((50, 600), subtitle, fill=self.accent_color, font=subtitle_font)
        
        # Save thumbnail
        timestamp = datetime.now().strftime('%Y-%m-%d')
        os.makedirs(output_path, exist_ok=True)
        output_file = os.path.join(output_path, f'{timestamp}_thumbnail.jpg')
        
        img.save(output_file, 'JPEG', quality=95)
        
        logger.info(f'Thumbnail saved: {output_file}')
        
        return output_file

if __name__ == '__main__':
    generator = ThumbnailGenerator()
    thumb = generator.create_thumbnail('ChatGPT for Budgeting: Save 00/Month')
    print(f"Thumbnail created: {thumb}")
