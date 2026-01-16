# WiseVirgin - Scripture Meditation Video Automation

Automated system for creating peaceful meditation videos with Bible verses overlaid on beautiful nature footage.

## What It Does

Creates meditation videos featuring:
- 📖 **Scripture Verses** - Beautiful Bible verses on themes like peace, faith, hope
- 🌿 **Nature Footage** - Peaceful videos of forests, rivers, oceans, mountains
- 🎵 **Peaceful Music** - Calming background music (royalty-free)
- ✨ **No Voiceover** - Just text, nature, and music

## Quick Start

### 1. Configure API Keys

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```
OPENAI_API_KEY=your_key_here       # For scripture generation
PEXELS_API_KEY=your_key_here       # For nature videos (free at pexels.com)
```

### 2. Add Background Music

Place your royalty-free peaceful music file:
```bash
mkdir -p output/cache/music
# Add your music file: output/cache/music/peaceful_music.mp3
```

**Free music sources:**
- YouTube Audio Library: https://studio.youtube.com/channel/UC/music
- Pixabay Music: https://pixabay.com/music/
- Free Music Archive: https://freemusicarchive.org/

### 3. Create a Test Video

```bash
cd /root/wisevirgin
source venv/bin/activate
python3 test_meditation.py              # Test components
python3 orchestrator/meditation_main.py  # Create full video
```

## Video Creation Process

The system follows this workflow:

1. **Scripture Generation** - Creates 10 Bible verses on a daily theme
2. **Nature Videos** - Downloads peaceful nature footage from Pexels
3. **Music** - Uses your peaceful background music
4. **Video Assembly** - Overlays scripture on nature videos with music
5. **YouTube Upload** - Uploads to your channel automatically

## Daily Themes

The system rotates through 8 themes:
- Peace and rest
- God's love and grace
- Faith and trust
- Hope and encouragement
- Joy and gratitude
- Strength and courage
- Forgiveness and mercy
- Wisdom and guidance

## Customization

### Change Video Duration

Edit `orchestrator/meditation_main.py`:
```python
result = orchestrator.create_meditation_video(
    theme=theme,
    duration=300,      # 5 minutes (change this)
    verse_count=10     # 10 verses (change this)
)
```

### Add More Themes

Edit `orchestrator/meditation_main.py`:
```python
themes = [
    'your custom theme 1',
    'your custom theme 2',
    # ...
]
```

### Change Nature Search

Edit `engines/production/nature_asset_manager.py`:
```python
nature_queries = [
    'peaceful river flowing',
    'your custom search',
    # ...
]
```

## File Structure

```
wisevirgin/
├── engines/
│   ├── content/
│   │   ├── scripture_generator.py      # Generate Bible verses
│   │   └── seo_generator.py            # YouTube metadata
│   └── production/
│       ├── nature_asset_manager.py     # Download nature videos
│       ├── music_manager.py            # Manage background music
│       └── meditation_video_assembler.py  # Combine everything
├── orchestrator/
│   └── meditation_main.py              # Main automation script
├── output/
│   ├── videos/                         # Created videos
│   ├── overlays/scripture/             # Scripture overlay images
│   └── cache/
│       ├── nature_footage/             # Downloaded nature videos
│       └── music/                      # Background music
└── logs/                               # System logs
```

## Troubleshooting

### No nature videos found
- Check PEXELS_API_KEY in .env
- Get free key at: https://www.pexels.com/api/

### No music available
- Add music manually to: `output/cache/music/peaceful_music.mp3`

### No LLM client available
- Check OPENAI_API_KEY in .env
- Scripture generator will use fallback verses if not configured

## Automation

Set up daily video creation:
```bash
crontab -e
# Add: 0 6 * * * /root/wisevirgin/orchestrator/daily_runner.sh
```

Creates one video daily at 6 AM.

## Project Origin

WiseVirgin was cloned from smart-money-automation and customized for meditation videos.
- Original: Talk-based financial education videos
- WiseVirgin: Peaceful scripture meditation videos

## Support

See documentation:
- MTT (Session tracker): `docs/MTT.md`
- CRI (Code patterns): `docs/CRI.md`
- QRI (FAQ): `docs/QRI.md`
