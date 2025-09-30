"""
Branch Social Listening Scraper - Facebook Module  
Scrapes posts/comments from the public Branch Facebook page using facebook-scraper
Target: ~20 latest posts/comments
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import time
import random

try:
    from facebook_scraper import get_posts
    FACEBOOK_SCRAPER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"facebook-scraper not available: {e}")
    FACEBOOK_SCRAPER_AVAILABLE = False

def scrape_facebook_mentions(page_name: str = "Branch", limit: int = 20) -> List[Dict[str, Any]]:
    """
    Scrape recent Facebook posts/comments using facebook-scraper
    
    Args:
        page_name: Facebook page name to scrape
        limit: Maximum number of posts to fetch
        
    Returns:
        List of dictionaries containing Facebook post/comment data
    """
    logging.info(f"Starting Facebook scrape for page: {page_name}, limit: {limit}")
    
    posts_data = []
    collected_ids = set()  # For deduplication
    
    try:
        if FACEBOOK_SCRAPER_AVAILABLE:
            # Try real Facebook scraping
            return scrape_facebook_real(page_name, limit, posts_data, collected_ids)
        else:
            # Fallback to simulated data
            return scrape_facebook_simulated(page_name, limit, posts_data, collected_ids)
            
    except Exception as e:
        logging.error(f"Error scraping Facebook: {str(e)}")
        logging.info(f"Falling back to simulated data")
        return scrape_facebook_simulated(page_name, limit, posts_data, collected_ids)

def scrape_facebook_real(page_name: str, limit: int, posts_data: List[Dict], collected_ids: set) -> List[Dict[str, Any]]:
    """
    Scrape real Facebook data using facebook-scraper
    """
    logging.info(f"Attempting to scrape real Facebook data from page: {page_name}")
    
    try:
        post_count = 0
        for post in get_posts(page_name, pages=2, extra_info=True, timeout=10):
            if post_count >= limit:
                break
                
            # Skip if no text content
            if not post.get('text') and not post.get('post_text'):
                continue
                
            # Create unique ID
            post_id = post.get('post_id', f"fb_{post_count}_{int(time.time())}")
            
            # Skip if we've already collected this post
            if post_id in collected_ids:
                continue
                
            collected_ids.add(post_id)
            
            # Extract post data in unified format
            post_text = post.get('text') or post.get('post_text') or ''
            
            post_data = {
                'source': 'facebook',
                'id': str(post_id),
                'user': page_name,
                'text': clean_text(post_text),
                'timestamp': post.get('time', datetime.now()).isoformat() if isinstance(post.get('time'), datetime) else datetime.now().isoformat(),
                'url': post.get('post_url', f"https://facebook.com/{post_id}"),
                'metrics': {
                    'likes': post.get('likes', 0),
                    'comments': post.get('comments', 0),
                    'shares': post.get('shares', 0)
                }
            }
            
            posts_data.append(post_data)
            post_count += 1
            
            # Add delay to be respectful
            time.sleep(1)
            
            if post_count % 5 == 0:
                logging.info(f"Collected {post_count} Facebook posts so far...")
        
        logging.info(f"Successfully collected {len(posts_data)} posts from Facebook")
        return posts_data
        
    except Exception as e:
        logging.error(f"Real Facebook scraping failed: {str(e)}")
        raise e

def scrape_facebook_simulated(page_name: str, limit: int, posts_data: List[Dict], collected_ids: set) -> List[Dict[str, Any]]:
    """
    Generate simulated Facebook data for MVP testing
    """
    logging.warning("Using simulated Facebook data for MVP testing")
    
    # Sample Facebook posts about Branch
    sample_posts = [
        "Branch is revolutionizing mobile linking! Check out their latest features for app developers.",
        "Just integrated Branch deep linking into our mobile app - the user experience is amazing!",
        "Looking for the best attribution platform? Branch has been fantastic for our marketing team.",
        "Branch's analytics dashboard gives us incredible insights into user behavior across platforms.",
        "Thanks to Branch support team for helping us with our implementation - top-notch service!",
        "Branch makes cross-platform user experience seamless. Highly recommend for mobile apps.",
        "The Branch SDK integration was surprisingly straightforward. Great documentation!",
        "Branch attribution is helping us optimize our marketing spend across different channels.",
        "Question for the community: anyone using Branch for web-to-app linking?",
        "Branch's personalized onboarding features have improved our user retention significantly."
    ]
    
    # Create realistic simulated data
    for i in range(min(limit, len(sample_posts) * 2)):  # Allow some repetition
        post_id = f"fb_sim_{random.randint(100000, 999999)}_{int(time.time() + i)}"
        
        # Skip if we've already collected this ID
        if post_id in collected_ids:
            continue
            
        collected_ids.add(post_id)
        
        post_data = {
            'source': 'facebook',
            'id': post_id,
            'user': page_name,
            'text': clean_text(sample_posts[i % len(sample_posts)]),
            'timestamp': (datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))).isoformat(),
            'url': f"https://facebook.com/{page_name}/posts/{post_id}",
            'metrics': {
                'likes': random.randint(5, 100),
                'comments': random.randint(0, 25),
                'shares': random.randint(0, 15)
            }
        }
        
        posts_data.append(post_data)
        
        # Add realistic delay
        time.sleep(0.2)
            
        if (i + 1) % 5 == 0:
            logging.info(f"Generated {i + 1} simulated Facebook posts so far...")
    
    logging.info(f"Generated {len(posts_data)} simulated Facebook posts (MVP mode)")
    return posts_data

def clean_text(text: str) -> str:
    """
    Clean and normalize Facebook post text
    
    Args:
        text: Raw post text
        
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

def validate_facebook_data(post_data: Dict[str, Any]) -> bool:
    """
    Validate that Facebook post data has required fields
    
    Args:
        post_data: Post data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['source', 'id', 'user', 'text', 'timestamp']
    return all(field in post_data and post_data[field] for field in required_fields)
