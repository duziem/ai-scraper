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
            posts = scrape_facebook_mentions(page_name=facebook_page, limit=20)
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
        
        # Save results for backup
        logger.info("💾 Saving collected mentions for backup...")
        import json
        with open('collected_mentions.json', 'w', encoding='utf-8') as f:
            json.dump({
                'mentions': sorted_mentions,
                'summary': summary,
                'collection_timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Stage 2 Complete: Data collection and processing finished")
        
        # Stage 3: Sentiment analysis and storage
        logger.info("=== Stage 3: Starting sentiment analysis and storage ===")
        
        if not sorted_mentions:
            logger.warning("No mentions available for sentiment analysis")
        else:
            try:
                # Import Stage 3 modules
                from analyze.sentiment import analyze_sentiment
                from store.sheets import append_to_google_sheet, test_google_sheets_connection
                
                # Extract text content for sentiment analysis
                texts_for_analysis = []
                for mention in sorted_mentions:
                    text = mention.get('text') or mention.get('content', '')
                    texts_for_analysis.append(text)
                
                logger.info(f"🧠 Running sentiment analysis on {len(texts_for_analysis)} texts...")
                
                # Perform sentiment analysis
                sentiment_results = analyze_sentiment(texts_for_analysis)
                
                if sentiment_results:
                    # Combine original data with sentiment results
                    analyzed_mentions = []
                    for i, mention in enumerate(sorted_mentions):
                        # Create copy of mention data
                        analyzed_mention = mention.copy()
                        
                        # Add sentiment results
                        if i < len(sentiment_results):
                            sentiment_data = sentiment_results[i]
                            analyzed_mention['sentiment_label'] = sentiment_data.get('sentiment_label', 'neutral')
                            analyzed_mention['sentiment_score'] = sentiment_data.get('sentiment_score', 0.5)
                            
                            # Include additional sentiment metadata if available
                            if 'all_scores' in sentiment_data:
                                analyzed_mention['sentiment_all_scores'] = sentiment_data['all_scores']
                            if 'error' in sentiment_data:
                                analyzed_mention['sentiment_error'] = sentiment_data['error']
                        else:
                            # Fallback for missing sentiment data
                            analyzed_mention['sentiment_label'] = 'neutral'
                            analyzed_mention['sentiment_score'] = 0.5
                        
                        analyzed_mentions.append(analyzed_mention)
                    
                    logger.info(f"✅ Sentiment analysis completed for {len(analyzed_mentions)} mentions")
                    
                    # Test Google Sheets connection
                    logger.info("🔗 Testing Google Sheets connection...")
                    if test_google_sheets_connection():
                        # Store results in Google Sheets
                        logger.info("📊 Storing analyzed data in Google Sheets...")
                        sheets_success = append_to_google_sheet(analyzed_mentions)
                        
                        if sheets_success:
                            logger.info("✅ Data successfully stored in Google Sheets")
                        else:
                            logger.error("❌ Failed to store data in Google Sheets")
                    else:
                        logger.error("❌ Google Sheets connection test failed - skipping storage")
                        logger.info("💡 Please check your GOOGLE_SERVICE_ACCOUNT_FILE environment variable")
                    
                    logger.info("Stage 3 Complete: Sentiment analysis and storage finished")
                    
                    # Save analyzed data for Stage 4
                    analyzed_data = {
                        'mentions': analyzed_mentions,
                        'summary': summary,
                        'sentiment_summary': {
                            'total_analyzed': len(analyzed_mentions),
                            'sentiment_distribution': {}
                        },
                        'analysis_timestamp': datetime.now().isoformat()
                    }
                    
                    # Calculate sentiment distribution
                    for mention in analyzed_mentions:
                        label = mention.get('sentiment_label', 'neutral')
                        analyzed_data['sentiment_summary']['sentiment_distribution'][label] = \
                            analyzed_data['sentiment_summary']['sentiment_distribution'].get(label, 0) + 1
                    
                    with open('analyzed_mentions.json', 'w', encoding='utf-8') as f:
                        json.dump(analyzed_data, f, indent=2, ensure_ascii=False)
                    
                else:
                    logger.error("❌ Sentiment analysis returned no results")
                    
            except ImportError as e:
                logger.error(f"❌ Failed to import Stage 3 modules: {e}")
            except Exception as e:
                logger.error(f"❌ Stage 3 failed with error: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Stage 4: Alerting and final processing
        logger.info("=== Stage 4: Starting alerting and automation ===")
        
        try:
            # Import Stage 4 modules
            from analyze.sentiment import calculate_sentiment_threshold
            from alerts.slack import send_slack_alert, test_slack_webhook
            
            # Get threshold from environment (default 20%)
            threshold_str = os.getenv('NEGATIVE_SENTIMENT_THRESHOLD', '0.20')
            try:
                threshold = float(threshold_str)
            except ValueError:
                logger.warning(f"Invalid threshold value '{threshold_str}', using default 0.20")
                threshold = 0.20
            
            logger.info(f"🎯 Using negative sentiment threshold: {threshold:.1%}")
            
            # Check if we have analyzed mentions for alerting
            if sorted_mentions and 'analyzed_mentions' in locals():
                # Calculate sentiment threshold
                logger.info("🧮 Calculating sentiment threshold for alerting...")
                threshold_crossed, negative_percentage, top_negative_mentions = calculate_sentiment_threshold(
                    analyzed_mentions, threshold
                )
                
                logger.info(f"📊 Threshold analysis: {negative_percentage:.1%} negative (threshold: {threshold:.1%})")
                
                if threshold_crossed and top_negative_mentions:
                    logger.warning(f"🚨 Negative sentiment threshold exceeded: {negative_percentage:.1%}")
                    logger.info(f"📋 Preparing alert with {len(top_negative_mentions)} top negative mentions")
                    
                    # Test Slack webhook first
                    logger.info("🧪 Testing Slack webhook connection...")
                    if test_slack_webhook():
                        # Send alert
                        logger.info("🔔 Sending Slack alert...")
                        alert_success = send_slack_alert(
                            negative_percentage=negative_percentage,
                            top_negative_mentions=top_negative_mentions,
                            total_mentions=len(analyzed_mentions)
                        )
                        
                        if alert_success:
                            logger.info("✅ Slack alert sent successfully")
                        else:
                            logger.error("❌ Failed to send Slack alert")
                    else:
                        logger.error("❌ Slack webhook test failed - skipping alert")
                        logger.info("💡 Please check your SLACK_WEBHOOK_URL environment variable")
                        
                else:
                    logger.info(f"✅ Negative sentiment below threshold ({negative_percentage:.1%} < {threshold:.1%}) - no alert needed")
                    
            else:
                logger.warning("⚠️  No analyzed mentions available for alerting")
                if not sorted_mentions:
                    logger.warning("   - No mentions were collected")
                else:
                    logger.warning("   - Stage 3 (sentiment analysis) may have failed")
            
            logger.info("Stage 4 Complete: Alerting and automation finished")
            
        except ImportError as e:
            logger.error(f"❌ Failed to import Stage 4 modules: {e}")
        except Exception as e:
            logger.error(f"❌ Stage 4 failed with error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"=== Branch Social Listening Scraper MVP Completed in {duration} ===")
        
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
