# WiseVirgin Codebase Reference Index (CRI)

**Type:** Code Pattern Cross-Reference Guide
**Scope:** PROJECT-SPECIFIC (WiseVirgin only)
**Version:** 1.0
**Last Updated:** 2026-01-15
**Owner:** MtaahVentures
**Project:** WiseVirgin Automation

---

## Purpose

FAQ-style index mapping code questions to real working examples from WiseVirgin codebase.

**Use this when:** You need to implement something in WiseVirgin but don't know how it's done in existing code.

**Note:** WiseVirgin is cloned from smart-money-automation - all code patterns from that project are available here.

---

## How to Use This Index

**Method 1: Search by question**
- Find your question in Column 1
- Column 2 shows real file paths from WiseVirgin codebase
- Open those files to see how it's actually implemented

**Method 2: Search by keyword** (Recommended)
- Press Ctrl+F (or Cmd+F on Mac)
- Search for any keyword from Column 3
- Find matching code pattern → Open files in Column 2

**Table Format:**
- **Column 1:** FAQ question (what you're trying to implement)
- **Column 2:** Real file paths from WiseVirgin codebase (working examples)
- **Column 3:** Keywords found in those files (for Ctrl+F search)

---

## Script Cleaning & Text Processing

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I remove production notes from scripts before TTS? | `/root/wisevirgin/engines/content/script_cleaner.py` | clean_for_tts, re.sub, \\*\\*\\[.*?\\]\\*\\*, regex patterns, MULTILINE |
| How do I extract visual cues from scripts? | `/root/wisevirgin/engines/content/script_cleaner.py` | extract_production_notes, re.findall, \\[VISUAL CUE:(.*?)\\], IGNORECASE |
| How do I remove markdown formatting from text? | `/root/wisevirgin/engines/content/script_cleaner.py` | re.sub(r'\\*\\*([^*]+)\\*\\*', r'\\1'), remove bold, preserve text |
| How do I clean up multiple newlines? | `/root/wisevirgin/engines/content/script_cleaner.py` | re.sub(r'\\n{3,}', '\\n\\n'), re.sub(r'\\n\\s*\\n\\s*\\n', '\\n\\n'), strip() |
| How do I handle curly quotes in regex? | `/root/wisevirgin/engines/content/script_cleaner.py` | \\u2018, \\u2019, smart quotes, unicode characters |

---

## Visual Asset Generation

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I create presentation slides with PIL? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | generate_presentation_slide, Image.new('RGB', (1920, 1080)), ImageDraw.Draw, dark blue background |
| How do I create bullet point infographics? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | generate_infographic, draw.ellipse, bullet circles, centered text layout |
| How do I create calculation graphics? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | generate_calculation_graphic, savings calculations, green highlight, total display |
| How do I generate assets from script visual cues? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | generate_assets_from_visual_cues, parse visual cue content, type detection |
| How do I draw text centered on image with PIL? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | textbbox, (bbox[2] - bbox[0]) / 2, center_x calculation, draw.text |
| How do I wrap long text on images? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | textwrap.fill, width=40, max_width parameter |
| How do I use custom fonts in PIL? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | ImageFont.truetype('arial.ttf', 60), try/except for font loading |

---

## Text Overlay Generation

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I create semi-transparent overlays? | `/root/wisevirgin/engines/production/text_overlay_generator.py` | Image.new('RGBA'), background color #000000AA, alpha channel |
| How do I extract checklist items from scripts? | `/root/wisevirgin/engines/production/text_overlay_generator.py` | extract_screenshot_moments, re.findall, \\*\\*Step.*?:\\*\\*, checklist detection |
| How do I generate batch text overlays? | `/root/wisevirgin/engines/production/text_overlay_generator.py` | generate_text_overlays, enumerate moments, create_screenshot_overlay |
| How do I save PNG overlays with transparency? | `/root/wisevirgin/engines/production/text_overlay_generator.py` | img.save(output_file, 'PNG'), RGBA mode, transparency preserved |

---

## Video Assembly with Visual Assets

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I mix visual assets with stock footage? | `/root/wisevirgin/engines/production/video_assembler.py` | assemble_video_with_visual_assets, i % 4 == 0, visual_asset_index |
| How do I convert static images to video clips? | `/root/wisevirgin/engines/production/video_assembler.py` | image_to_video, ffmpeg -loop 1 -i, -t duration, -c:v libx264 |
| How do I composite text overlays onto video? | `/root/wisevirgin/engines/production/video_assembler.py` | add_text_overlays, ffmpeg overlay filter, overlay=0:0, enable='between(t,X,Y)' |
| How do I time overlays to specific timestamps? | `/root/wisevirgin/engines/production/video_assembler.py` | enable=between(t,start,end), start_time calculation, duration |
| How do I concatenate heterogeneous video segments? | `/root/wisevirgin/engines/production/video_assembler.py` | concat protocol, file list.txt, -safe 0 -f concat |

---

## API Integration Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I integrate OpenAI API for script generation? | `/root/wisevirgin/utils/free_llm_client.py` | OpenAI, client.chat.completions.create, gpt-4o-mini, max_tokens, temperature |
| How do I call Pexels API for stock footage? | `/root/wisevirgin/engines/production/asset_manager.py` | requests.get, api.pexels.com/videos/search, Authorization header, video_files, link |
| How do I use YouTube Data API for uploads? | `/root/wisevirgin/engines/publishing/youtube_uploader.py` | googleapiclient.discovery.build, videos().insert, MediaFileUpload, resumable=True |
| How do I authenticate YouTube with existing tokens? | `/root/wisevirgin/utils/youtube_api.py` | pickle.load, credentials_1_token.pickle, build('youtube', 'v3') |
| How do I scrape YouTube transcripts? | `/root/wisevirgin/engines/content/script_research.py` | YouTubeTranscriptApi.get_transcript, video_id, extract_video_id |
| How do I use Google Trends API? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | pytrends, TrendReq, build_payload, interest_over_time, timeframe='now 7-d' |
| How do I query Reddit API? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | praw, Reddit, subreddit().hot, limit=25, created_utc |

---

## Video Production Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I generate voiceover with TTS? | `/root/wisevirgin/engines/production/tts_engine.py` | edge_tts, Communicate, en-US-JennyNeural, en-US-GuyNeural, await communicate.save |
| How do I clean scripts before TTS? | `/root/wisevirgin/engines/production/tts_engine.py` | script_cleaner.clean_for_tts, len(script) -> len(clean_script), logging |
| How do I download stock video clips? | `/root/wisevirgin/engines/production/asset_manager.py` | requests.get(video_url, stream=True), iter_content, chunk_size=8192 |
| How do I assemble video with FFmpeg? | `/root/wisevirgin/engines/production/video_assembler.py` | ffmpeg, -i, -ss, -t, -c:v libx264, -c:a aac, concat |
| How do I create thumbnails with Pillow? | `/root/wisevirgin/engines/production/thumbnail_gen.py` | PIL, Image.new, ImageDraw, ImageFont, truetype, textbbox, img.save |
| How do I calculate video duration from audio? | `/root/wisevirgin/engines/production/video_assembler.py` | ffprobe, -show_entries format=duration, json.loads |

---

## Database & Tracking Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I create SQLite database for tracking? | `/root/wisevirgin/engines/publishing/publish_tracker.py` | sqlite3.connect, CREATE TABLE IF NOT EXISTS, TEXT, INTEGER, TIMESTAMP |
| How do I insert video metadata into database? | `/root/wisevirgin/engines/publishing/publish_tracker.py` | cursor.execute, INSERT OR REPLACE, video_id, json.dumps, conn.commit |
| How do I query video performance data? | `/root/wisevirgin/engines/publishing/publish_tracker.py` | SELECT * FROM videos, fetchall(), ORDER BY publish_date DESC |
| How do I save JSON data to file? | `/root/wisevirgin/engines/opportunity/topic_scorer.py` | json.dump, open(file, 'w'), ensure_ascii=False, indent=2 |

---

## Content Generation Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I generate SEO-optimized titles? | `/root/wisevirgin/engines/content/seo_generator.py` | generate_title, f-string template, capitalize, colon formatting |
| How do I create YouTube descriptions? | `/root/wisevirgin/engines/content/seo_generator.py` | generate_description, multi-line f-string, timestamps, call-to-action |
| How do I generate video tags? | `/root/wisevirgin/engines/content/seo_generator.py` | broad + specific tags list, keyword variations, return tags[:30] |
| How do I build AI prompts for script generation? | `/root/wisevirgin/engines/content/script_generator.py` | build_prompt, f-string template, system/user messages, context injection |

---

## Trend Monitoring Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I fetch Google Trends data? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | pytrends.build_payload, interest_over_time(), df.iloc[-1], velocity calculation |
| How do I scrape Reddit hot posts? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | reddit.subreddit().hot(limit=25), submission.score, created_utc, time.time() |
| How do I parse Product Hunt RSS feed? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | feedparser.parse, entries, published_parsed, time.mktime |
| How do I get YouTube autocomplete suggestions? | `/root/wisevirgin/engines/opportunity/keyword_research.py` | suggestqueries.google.com, client=youtube, ds=yt, json() |
| How do I analyze YouTube competition? | `/root/wisevirgin/engines/opportunity/keyword_research.py` | youtube.search().list, part='snippet', maxResults=50, publishedAfter |
| How do I score opportunities 0-100? | `/root/wisevirgin/engines/opportunity/topic_scorer.py` | trend_velocity_score, search_interest_score, competition_score, recency_bonus |

---

## Orchestration & Pipeline Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I coordinate multi-phase pipeline? | `/root/wisevirgin/orchestrator/main.py` | WiseVirginOrchestrator, run_full_pipeline, phase1, phase2, phase3, phase4, phase5 |
| How do I integrate visual asset generation? | `/root/wisevirgin/orchestrator/main.py` | VisualAssetGenerator, generate_assets_from_visual_cues, visual_cues from script |
| How do I integrate text overlay generation? | `/root/wisevirgin/orchestrator/main.py` | TextOverlayGenerator, generate_text_overlays, extract moments from script |
| How do I coordinate video + overlays? | `/root/wisevirgin/orchestrator/main.py` | assemble_video_with_visual_assets, then add_text_overlays, two-pass processing |
| How do I load environment variables? | `/root/wisevirgin/orchestrator/main.py` | from dotenv import load_dotenv, load_dotenv(), os.getenv |
| How do I run automation via cron job? | `/root/wisevirgin/orchestrator/daily_runner.sh` | source venv/bin/activate, python3 orchestrator/main.py, deactivate |

---

## Logging & Error Handling Patterns

| FAQ Question | Real Codebase Examples | Keywords |
|--------------|------------------------|----------|
| How do I set up centralized logging? | `/root/wisevirgin/utils/logging_utils.py` | setup_logger, logging.getLogger, StreamHandler, FileHandler, logging.INFO |
| How do I create daily log files? | `/root/wisevirgin/utils/logging_utils.py` | get_daily_log_file, datetime.now().strftime, os.makedirs, exist_ok=True |
| How do I handle API errors? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | try/except, logger.error, logger.warning, return empty list |
| How do I log script cleaning stats? | `/root/wisevirgin/engines/production/tts_engine.py` | logger.info(f'Cleaned script: {len(script)} -> {len(clean_script)} characters') |

---

## Maintaining This Index

**When you say "update MTT, CRI, and QRI":**

1. **Update wisevirginMTT.md** - Session work completed
2. **Update wisevirginCRI.md** - New code patterns (if any)
3. **Update wisevirginQRI.md** - New FAQs (if any)

**Add entries when:**
- Implementing new features
- Discovering useful code patterns
- Creating new engines or modules
- Adding new API integrations
- Solving complex implementation challenges

---

## Related Documentation

**Project Documentation:**
- `/root/wisevirgin/README.md` - Project overview
- `/root/wisevirgin/PRODUCTION_READY.md` - Deployment status
- `/root/wisevirgin/.env.example` - Environment variables template
- `wisevirginMTT.md` - Session work tracker
- `wisevirginQRI.md` - FAQ index

**Source Project (Reference):**
- `/root/smart-money-automation/` - Original project this was cloned from
- `/root/smart-money-automation/docs/CRI.md` - Source CRI reference

**SOPs:**
- `C:\Users\myeku\SOPs\1-ORGANIZATION\ORG-SOP-009-MTT-CRI-QRI-Management-Workflow.md`
- `C:\Users\myeku\SOPs\3-PLATFORMS\GITHUB\GITHUB-SOP-005-Git-Push-Workflow.md`
- `C:\Users\myeku\SOPs\2-ENVIRONMENTS\VPS\VPS-SOP-002-Secrets-Password-Management.md`

**External Resources:**
- Pillow Documentation: https://pillow.readthedocs.io/
- FFmpeg Overlay Filter: https://ffmpeg.org/ffmpeg-filters.html#overlay
- Regex Patterns: https://docs.python.org/3/library/re.html

---

**Last Updated:** 2026-01-15
**Version:** 1.0
**Status:** Initial creation (cloned from smart-money-automation)
**Maintained by:** WiseVirgin Claude Code sessions

---

**Quick Tip:** Use Ctrl+F to search keywords in Column 3 to quickly find relevant code examples
