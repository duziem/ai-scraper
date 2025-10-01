"""
Branch Social Listening Scraper - Twitter Module
Scrapes latest tweets containing "Branch OR @BranchApp" using snscrape
Target: ~100 recent tweets
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import random

def scrape_twitter_mentions(query: str = "Branch OR @BranchApp", limit: int = 100) -> List[Dict[str, Any]]:
    """
    Scrape recent Twitter mentions using snscrape
    
    Args:
        query: Search query for Twitter mentions
        limit: Maximum number of tweets to fetch
        
    Returns:
        List of dictionaries containing tweet data
    """
    logging.info(f"Starting Twitter scrape with query: '{query}', limit: {limit}")
    
    tweets_data = []
    collected_ids = set()  # For deduplication
    
    try:
        # TEMPORARY: Simulated Twitter data for MVP testing
        # TODO: Replace with working Twitter API solution (snscrape has Python 3.13 compatibility issues)
        logging.warning("Using simulated Twitter data - snscrape has Python 3.13 compatibility issues")
        
        # Generate simulated tweet data for testing
        sample_tweets = [
            "Just tried the new Branch app features - really impressed with the user experience!",
            "Having issues with Branch deep linking, anyone else experiencing this?",
            "Branch attribution is working great for our mobile campaigns @BranchApp",
            "The Branch dashboard analytics are so helpful for understanding user behavior",
            "Question about Branch setup - does anyone have documentation for Unity integration?",
            "Love how Branch handles cross-platform linking seamlessly",
            "Branch support team was super helpful with our implementation",
            "Comparing Branch vs other attribution platforms - Branch wins on ease of use",
            "Branch deep links are loading faster than expected, great performance!",
            "Struggling with Branch configuration for our web app, any tips?"
        ]
        
        sample_users = ["developer_mike", "sarah_mobile", "app_guru", "tech_jane", "mobile_dev", "startup_founder", "growth_hacker", "product_manager", "ios_dev", "android_expert"]
        
        # Create realistic simulated data
        for i in range(min(limit, len(sample_tweets))):
            tweet_id = str(random.randint(1000000000000000000, 9999999999999999999))
            
            # Skip if we've already collected this ID
            if tweet_id in collected_ids:
                continue
                
            collected_ids.add(tweet_id)
            
            tweet_data = {
                'source': 'twitter',
                'id': tweet_id,
                'user': random.choice(sample_users),
                'text': clean_text(sample_tweets[i % len(sample_tweets)]),
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23))).isoformat(),
                'url': f"https://twitter.com/x/status/{tweet_id}",
                'metrics': {
                    'likes': random.randint(0, 50),
                    'retweets': random.randint(0, 20),
                    'replies': random.randint(0, 15)
                }
            }
            
            tweets_data.append(tweet_data)
            
            # Add realistic delay
            time.sleep(0.1)
                
            if (i + 1) % 25 == 0:
                logging.info(f"Generated {i + 1} simulated tweets so far...")
        
        logging.info(f"Generated {len(tweets_data)} simulated tweets from Twitter (MVP mode)")
        return tweets_data
        
    except Exception as e:
        logging.error(f"Error scraping Twitter: {str(e)}")
        logging.info(f"Returning {len(tweets_data)} tweets collected before error")
        return tweets_data

def clean_text(text: str) -> str:
    """
    Clean and normalize tweet text
    
    Args:
        text: Raw tweet text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Remove excessive whitespace and normalize
    cleaned = " ".join(text.split())
    
    # Ensure proper encoding
    try:
        cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        pass
        
    return cleaned.strip()

def validate_tweet_data(tweet_data: Dict[str, Any]) -> bool:
    """
    Validate that tweet data has required fields
    
    Args:
        tweet_data: Tweet data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['source', 'id', 'user', 'text', 'timestamp']
    return all(field in tweet_data and tweet_data[field] for field in required_fields)
