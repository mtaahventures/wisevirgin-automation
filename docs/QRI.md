# WiseVirgin Quick Reference Index (QRI)

**Type:** FAQ-Style Cross-Reference Guide
**Scope:** PROJECT-SPECIFIC (WiseVirgin only)
**Version:** 1.0
**Last Updated:** 2026-01-15
**Owner:** MtaahVentures
**Project:** WiseVirgin Automation

---

## Purpose

FAQ-style index for WiseVirgin mapping questions to documentation with searchable keywords.

**Use this when:** You have a question specific to WiseVirgin implementation.

**Note:** WiseVirgin is cloned from smart-money-automation - all documentation patterns from that project apply here.

---

## How to Use This Index

**Method 1:** Browse FAQ questions in Column 1
**Method 2:** Press Ctrl+F and search keywords in Column 3
**Method 3:** Search by error message

**Table Format:**
- **Column 1:** FAQ question (focused, searchable)
- **Column 2:** Documentation or file location
- **Column 3:** Keywords for Ctrl+F search

---

## Project Setup & Configuration

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How do I set up the project from scratch? | `/root/wisevirgin/README.md` | git clone, python3 -m venv, pip install -r requirements.txt, .env setup |
| What environment variables are needed? | `/root/wisevirgin/.env.example` | OPENAI_API_KEY, PEXELS_API_KEY, REDDIT_CLIENT_ID, YouTube credentials |
| Where do I get OpenAI API key? | `/root/wisevirgin/.env.example` | platform.openai.com/api-keys, gpt-4o-mini, $0.01 per video |
| Where do I get Pexels API key? | `/root/wisevirgin/.env.example` | pexels.com/api, free tier, 200 requests/hour |
| How do I configure YouTube authentication? | `/root/wisevirgin/utils/youtube_api.py` | /root/youtube_tokens/, credentials_1_token.pickle, pickle.load |
| What Python version is required? | `/root/wisevirgin/requirements.txt` | Python 3.12.3, google-api-python-client, openai, edge-tts |
| Where is the project located on VPS? | `wisevirginMTT.md` - Quick Notes | /root/wisevirgin/, cloned from smart-money-automation |

---

## Deployment & Operations

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How do I deploy to VPS? | `/root/wisevirgin/PRODUCTION_READY.md` | VPS location /root/wisevirgin, cron job, daily automation |
| What is the cron job schedule? | `/root/wisevirgin/orchestrator/daily_runner.sh` | 0 6 * * *, 6:00 AM EST, daily uploads |
| How do I test the system without API costs? | `/root/wisevirgin/test_system.py` | python3 test_system.py, 5/5 phases, no API calls |
| How do I run a dry run simulation? | `/root/wisevirgin/dry_run_test.py` | python3 dry_run_test.py, API key verification, no video creation |
| How do I manually create a video? | `/root/wisevirgin/PRODUCTION_READY.md` | cd /root/wisevirgin, source venv/bin/activate, python3 orchestrator/main.py |
| Where are logs stored? | `/root/wisevirgin/orchestrator/daily_runner.sh` | logs/cron.log, logs/daily_run_YYYY-MM-DD.log |

---

## Architecture & Design

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| What is the 5-phase architecture? | `/root/wisevirgin/README.md` | Phase 1 Opportunity, Phase 2 Content, Phase 3 Production, Phase 4 Publishing, Phase 5 Intelligence |
| How does the modular design work? | `wisevirginCRI.md` | standalone engines, reusable components, clear inputs/outputs |
| What project is this cloned from? | `wisevirginMTT.md` - Quick Notes | smart-money-automation, /root/smart-money-automation/, complete clone |
| What components are inherited? | `wisevirginMTT.md` - Code Changes | ScriptCleaner, VisualAssetGenerator, TextOverlayGenerator, all 5 phases |

---

## API Keys & Credentials

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| Where is OpenAI API key stored? | `VPS-SOP-002-Secrets-Password-Management.md` | secret-get credentials prod, OPENAI_API_KEY, vault |
| How many YouTube accounts can I use? | `wisevirginMTT.md` - Configuration | 3 accounts, /root/youtube_tokens/, credentials_1_token.pickle |
| Are Reddit API credentials required? | `/root/wisevirgin/.env.example` | optional, fallback topics work, trend monitoring enhancement |
| Where do I configure Pexels API? | `/root/wisevirgin/.env.example` | PEXELS_API_KEY, free tier, 200 requests/hour |

---

## Phase 1: Opportunity Intelligence

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How does topic selection work? | `/root/wisevirgin/engines/opportunity/topic_scorer.py` | find_best_topic, 0-100 scoring, trend velocity, competition level |
| What trend sources are monitored? | `/root/wisevirgin/engines/opportunity/trend_monitor.py` | Google Trends, Reddit, Product Hunt, subreddits |
| How are keywords researched? | `/root/wisevirgin/engines/opportunity/keyword_research.py` | YouTube autocomplete, competition analysis, suggestqueries.google.com |
| What happens if no trends found? | `/root/wisevirgin/engines/opportunity/topic_scorer.py` | fallback topic, score=50 |
| Why am I getting Google Trends 429 errors? | `wisevirginMTT.md` - Issues/Blockers | Rate limiting, not critical, fallback topics work |

---

## Phase 2: Content Generation

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How are scripts generated? | `/root/wisevirgin/engines/content/script_generator.py` | OpenAI gpt-4o-mini, 1500 words, retention hooks, build_prompt |
| How are YouTube transcripts scraped? | `/root/wisevirgin/engines/content/script_research.py` | YouTubeTranscriptApi, get_transcript, video_id extraction |
| How are SEO titles generated? | `/root/wisevirgin/engines/content/seo_generator.py` | "[Tool] for [outcome] ([result])", template formatting |
| What script length is used? | `/root/wisevirgin/engines/content/script_generator.py` | 1200-1500 words, ~150 words per minute, 8-10 minute videos |

---

## Phase 3: Video Production

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| What TTS voice is used? | `/root/wisevirgin/engines/production/tts_engine.py` | en-US-JennyNeural, en-US-GuyNeural, Edge-TTS, 4 voices available, Microsoft free |
| How are production notes removed before TTS? | `/root/wisevirgin/engines/content/script_cleaner.py` | clean_for_tts, regex patterns, 15.7% reduction |
| What production notes are removed? | `wisevirginCRI.md` - Script Cleaning section | \\*\\*[INTRO]\\*\\*, [VISUAL CUE:], asterisk, Cut to, horizontal rules |
| How are visual assets created? | `/root/wisevirgin/engines/production/visual_asset_generator.py` | presentation slides, infographics, calculation graphics, PIL, 1920x1080 |
| What types of visual assets are generated? | `wisevirginCRI.md` - Visual Asset Generation | slides for prompts, infographics for tips, calculation graphics |
| How are text overlays created? | `/root/wisevirgin/engines/production/text_overlay_generator.py` | semi-transparent overlays, RGBA, checklist format |
| How is stock footage downloaded? | `/root/wisevirgin/engines/production/asset_manager.py` | Pexels API, 15-20 clips, landscape orientation, HD quality |
| How are videos assembled with visual assets? | `/root/wisevirgin/engines/production/video_assembler.py` | assemble_video_with_visual_assets, mix every 4th clip |
| How are text overlays composited? | `/root/wisevirgin/engines/production/video_assembler.py` | add_text_overlays, FFmpeg overlay filter, enable='between(t,X,Y)' |
| What thumbnail size is created? | `/root/wisevirgin/engines/production/thumbnail_gen.py` | 1280x720, JPEG quality=95, Pillow, text overlay |
| Where are videos cached? | `/root/wisevirgin/engines/production/asset_manager.py` | output/cache/stock_footage/, clip_1.mp4, clip_2.mp4 |

---

## Phase 4: Publishing & Distribution

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How are videos uploaded to YouTube? | `/root/wisevirgin/engines/publishing/youtube_uploader.py` | YouTube Data API v3, MediaFileUpload, resumable=True, progress tracking |
| What is the optimal publish time? | `/root/wisevirgin/engines/publishing/schedule_optimizer.py` | 6-8 PM EST, Mon-Thu, weekdays, [18, 19, 20] hours |
| How is video performance tracked? | `/root/wisevirgin/engines/publishing/publish_tracker.py` | SQLite database, data/published_videos.db, video_id, views, likes |
| Where is the tracking database? | `/root/wisevirgin/engines/publishing/publish_tracker.py` | data/published_videos.db, videos table, performance table |
| How do I switch YouTube accounts? | `/root/wisevirgin/engines/publishing/youtube_uploader.py` | account_number parameter, credentials_{account_number}_token.pickle |

---

## Phase 5: Intelligence & Learning

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How are analytics fetched? | `/root/wisevirgin/engines/intelligence/analytics.py` | YouTube Data API, get_video_stats, views, likes, comments, watch_time |
| How are patterns detected? | `/root/wisevirgin/engines/intelligence/pattern_detector.py` | analyze_performance, GROUP BY topic, top 5 performing topics |

---

## Testing & Validation

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| How do I run system tests? | `/root/wisevirgin/test_system.py` | python3 test_system.py, 5/5 phases, test_phase1, test_phase2 |
| What tests are performed? | `wisevirginMTT.md` - Testing Notes | Phase tests, API connectivity, dry run simulation, no API costs |

---

## Cost & Budget

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| What are the monthly costs? | `/root/wisevirgin/PRODUCTION_READY.md` | ~$5-10/month, OpenAI only paid, Pexels free, Edge-TTS free |
| How much does script generation cost? | `/root/wisevirgin/.env.example` | ~$0.01 per video, gpt-4o-mini, $5/month for daily |

---

## Troubleshooting

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| Error: "No module named 'googleapiclient'" | `wisevirginMTT.md` - Issues/Blockers | pip install google-api-python-client, requirements.txt update |
| Error: Pexels API returns 401 | `wisevirginMTT.md` - Testing Notes | Check PEXELS_API_KEY, .env configuration, Authorization header |
| Error: YouTube upload fails | `/root/wisevirgin/utils/youtube_api.py` | Check credentials_1_token.pickle, /root/youtube_tokens/, pickle.load |
| Error: YouTube quota exceeded | `wisevirginMTT.md` - Issues/Blockers | 6-10 video daily limit, switch to account 2 or 3, wait 24 hours |
| Error: OAuth invalid_grant | `wisevirginMTT.md` - Issues/Blockers | Token expired, regenerate OAuth token, or use alternative account |
| Why is Google Trends returning 0 trends? | `wisevirginMTT.md` - Issues/Blockers | 429 rate limiting, fallback topics activated, not critical |

---

## Project Cloning & Setup

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| What project is WiseVirgin cloned from? | `wisevirginMTT.md` - Quick Notes | smart-money-automation, /root/smart-money-automation/ |
| What was cleaned during cloning? | `wisevirginMTT.md` - Code Changes | .git removed, output/ cleared, data/ cleared, logs/ cleared, .env removed |
| What files were updated? | `wisevirginMTT.md` - Code Changes | README.md, PRODUCTION_READY.md, orchestrator/main.py, daily_runner.sh |
| Are all components from smart-money preserved? | `wisevirginMTT.md` - Code Changes | Yes, all 5 phases, all engines, ScriptCleaner, VisualAssetGenerator, TextOverlayGenerator |

---

## GitHub & Version Control

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| Where is the GitHub repository? | `wisevirginMTT.md` - Configuration | github.com/mtaahventures/wisevirgin, not yet created |
| How do I push to GitHub? | `GITHUB-SOP-005-Git-Push-Workflow.md` | git push origin master, credentials configured |

---

## Channel Information

| FAQ Question | Documentation/Location | Keywords |
|--------------|------------------------|----------|
| What is the target channel? | `wisevirginMTT.md` - Configuration | WiseVirgin Channel, awaiting configuration |
| What content niche? | `wisevirginMTT.md` - Next Steps | Awaiting user requirements, will customize from smart-money base |
| What video format? | `/root/wisevirgin/README.md` | Faceless, automated, stock footage + visual assets + TTS, daily uploads |

---

## Maintaining This Index

**When you say "update MTT, CRI, and QRI":**

1. **Update wisevirginMTT.md** - Session work completed
2. **Update wisevirginCRI.md** - New code patterns (if any)
3. **Update wisevirginQRI.md** - New FAQs (if any)

**Add entries when:**
- Implementing new features
- Solving new problems
- Creating new documentation
- Discovering useful patterns
- Answering recurring questions

---

## Related Documentation

**Project Files:**
- `/root/wisevirgin/README.md` - Main project documentation
- `/root/wisevirgin/PRODUCTION_READY.md` - Deployment checklist
- `/root/wisevirgin/.env.example` - Environment setup
- `wisevirginMTT.md` - Session work tracker
- `wisevirginCRI.md` - Code pattern index

**Source Project (Reference):**
- `/root/smart-money-automation/` - Original project
- `/root/smart-money-automation/docs/MTT.md` - Smart Money MTT
- `/root/smart-money-automation/docs/CRI.md` - Smart Money CRI
- `/root/smart-money-automation/docs/QRI.md` - Smart Money QRI

**SOPs:**
- `C:\Users\myeku\SOPs\1-ORGANIZATION\ORG-SOP-009-MTT-CRI-QRI-Management-Workflow.md`
- `C:\Users\myeku\SOPs\3-PLATFORMS\GITHUB\GITHUB-SOP-005-Git-Push-Workflow.md`
- `C:\Users\myeku\SOPs\2-ENVIRONMENTS\VPS\VPS-SOP-002-Secrets-Password-Management.md`

**External Resources:**
- https://www.pexels.com/api/documentation/ - Pexels API docs
- https://platform.openai.com/docs/ - OpenAI API docs
- https://developers.google.com/youtube/v3 - YouTube Data API docs
- https://github.com/rany2/edge-tts - Edge-TTS documentation
- https://pillow.readthedocs.io/ - Pillow (PIL) documentation
- https://ffmpeg.org/ffmpeg-filters.html#overlay - FFmpeg overlay filter

---

**Last Updated:** 2026-01-15
**Version:** 1.0
**Status:** Initial creation (cloned from smart-money-automation)
**Maintained by:** WiseVirgin Claude Code sessions

---

**Quick Tip:** Use Ctrl+F to search keywords in Column 3 to find answers instantly
