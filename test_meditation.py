#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append('/root/wisevirgin')

print('Testing Meditation Video Components...')
print('='*60)

# Test 1: Scripture Generator
print('\n1. Testing Scripture Generator...')
try:
    from engines.content.scripture_generator import ScriptureGenerator
    gen = ScriptureGenerator()
    result = gen.generate_scripture_collection('peace', 5)
    print(f'   ✅ Generated {len(result["verses"])} scripture verses')
    print(f'   Sample: {result["verses"][0][:60]}...')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 2: Nature Asset Manager
print('\n2. Testing Nature Asset Manager...')
try:
    from engines.production.nature_asset_manager import NatureAssetManager
    manager = NatureAssetManager()
    videos = manager.fetch_nature_videos('peaceful', 3)
    print(f'   ✅ Found {len(videos)} nature videos')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 3: Music Manager
print('\n3. Testing Music Manager...')
try:
    from engines.production.music_manager import MusicManager
    music_mgr = MusicManager()
    music = music_mgr.get_peaceful_music()
    if music:
        print(f'   ✅ Music: {music}')
    else:
        print(f'   ⚠️  No music (will need to add manually)')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 4: Meditation Video Assembler
print('\n4. Testing Meditation Video Assembler...')
try:
    from engines.production.meditation_video_assembler import MeditationVideoAssembler
    assembler = MeditationVideoAssembler()
    print(f'   ✅ Meditation assembler initialized')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 5: SEO Generator (Meditation)
print('\n5. Testing SEO Generator (Meditation)...')
try:
    from engines.content.seo_generator import SEOGenerator
    seo = SEOGenerator()
    metadata = seo.generate_meditation_metadata('peace and rest')
    print(f'   ✅ Title: {metadata["title"][:50]}...')
    print(f'   ✅ Tags: {len(metadata["tags"])} tags')
except Exception as e:
    print(f'   ❌ Error: {e}')

print('\n' + '='*60)
print('Component testing complete!')
print('='*60)
