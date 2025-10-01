#!/usr/bin/env python3
"""
Branch Social Listening Scraper - Main Execution Script
Orchestrates the complete pipeline: scrape → analyze → store → alert

Demo Success Criteria:
- Fetches 50+ mentions across 3 sources (Twitter, Facebook, Google Play)
- Runs sentiment analysis on collected data
- Logs results to Google Sheets
- Triggers Slack alert if ≥20% negative sentiment
"""

import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('branch_scraper.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main execution function for Branch Social Listening Scraper MVP
    """
    logger.info("=== Branch Social Listening Scraper MVP Started ===")
    start_time = datetime.now()
    
    try:
        # Import scrapers (inside function to avoid import errors during initialization)
        from scrapers.twitter import scrape_twitter_mentions
        from scrapers.facebook import scrape_facebook_mentions
        from scrapers.google_play import scrape_google_play_reviews
        from scrapers.data_processor import deduplicate_mentions, get_mentions_summary, sort_mentions_by_timestamp
        
        # Stage 2: Data collection from all sources
        logger.info("Stage 2: Starting data collection from all sources")
        
        all_mentions = []
        
        # Twitter scraping
        logger.info("Collecting Twitter mentions...")
        try:
            twitter_query = os.getenv('TWITTER_QUERY', 'Branch OR @BranchApp')
            tweets = scrape_twitter_mentions(query=twitter_query, limit=50)
            all_mentions.extend(tweets)
            logger.info(f"✅ Collected {len(tweets)} Twitter mentions")
        except Exception as e:
            logger.error(f"Twitter scraping failed: {e}")
        
        # Facebook scraping
        logger.info("Collecting Facebook mentions...")
        try:
            facebook_page = os.getenv('FACEBOOK_PAGE', 'Branch')
            posts = scrape_facebook_mentions(page_name=facebook_page, limit=10)
            all_mentions.extend(posts)
            logger.info(f"✅ Collected {len(posts)} Facebook mentions")
        except Exception as e:
            logger.error(f"Facebook scraping failed: {e}")
        
        # Google Play scraping
        logger.info("Collecting Google Play reviews...")
        try:
            google_play_app_id = os.getenv('GOOGLE_PLAY_APP_ID', 'io.branch.referral.branch')
            reviews = scrape_google_play_reviews(app_id=google_play_app_id, limit=25)
            all_mentions.extend(reviews)
            logger.info(f"✅ Collected {len(reviews)} Google Play reviews")
        except Exception as e:
            logger.error(f"Google Play scraping failed: {e}")
        
        # Data processing and deduplication
        logger.info(f"Processing {len(all_mentions)} total mentions...")
        deduplicated_mentions = deduplicate_mentions(all_mentions)
        sorted_mentions = sort_mentions_by_timestamp(deduplicated_mentions)
        
        # Generate summary
        summary = get_mentions_summary(sorted_mentions)
        logger.info(f"📊 Collection Summary:")
        logger.info(f"   Total mentions: {summary['total_mentions']}")
        logger.info(f"   By source: {summary['by_source']}")
        if summary['date_range']:
            logger.info(f"   Date range: {summary['date_range']['span_days']} days")
        
        # Save results for Stage 3 processing
        logger.info("💾 Saving collected mentions for sentiment analysis...")
        import json
        with open('collected_mentions.json', 'w', encoding='utf-8') as f:
            json.dump({
                'mentions': sorted_mentions,
                'summary': summary,
                'collection_timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Stage 2 Complete: Data collection and processing finished")
        
        # TODO: Stage 3 - Implement sentiment analysis and storage
        logger.info("Stage 3: Ready for sentiment analysis and storage (TODO)")
        
        # TODO: Stage 4 - Implement alerting logic
        logger.info("Stage 4: Ready for alerting implementation (TODO)")
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"=== Branch Social Listening Scraper MVP Completed in {duration} ===")
        
        # Exit successfully
        return 0
        
        # Exit successfully
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
