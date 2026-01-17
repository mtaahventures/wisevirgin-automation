#!/usr/bin/env python3
"""
Daily Medium Runner - Runs at 12:00 PM daily

Selects best opportunity and generates one 2-hour video
"""
import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))

from opportunity_selector import get_best_opportunity
from generate_medium import generate_medium_video
from utils.logging_utils import setup_logger, get_daily_log_file

logger = setup_logger("daily_medium", get_daily_log_file())

async def main():
    logger.info("="*80)
    logger.info(f"DAILY MEDIUM GENERATION - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("="*80)

    # Get best opportunity (with smart fallback)
    opportunity = get_best_opportunity(format_name="medium")

    # Generate and publish
    result = await generate_medium_video(
        event=opportunity['event'],
        emotion=opportunity['emotion'],
        content_type=opportunity['content_type'],
        score=opportunity['score']
    )

    if result:
        logger.info(f"✅ Daily medium published: {result['video_url']}")
        print(f"✅ SUCCESS: {result['video_url']}")
        return 0
    else:
        logger.error("❌ Generation failed")
        print("❌ FAILED: Generation failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
