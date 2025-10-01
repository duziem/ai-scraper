"""
Branch Social Listening Scraper - Slack Alerting Module
Uses Slack Incoming Webhooks for notifications
Triggers when ≥20% negative sentiment with top 3 negative texts
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import json

def format_alert_message(negative_percentage: float, top_negative_mentions: List[Dict[str, Any]], total_mentions: int = 0) -> Dict[str, Any]:
    """
    Format Slack message payload for negative sentiment alert using Block Kit
    
    Args:
        negative_percentage: Percentage of negative sentiment  
        top_negative_mentions: Top negative mentions to include
        total_mentions: Total number of mentions analyzed
        
    Returns:
        Dictionary containing Slack message payload
    """
    logging.info(f"🎨 Formatting Slack alert message for {negative_percentage:.1%} negative sentiment")
    
    try:
        # Format timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Create header block
        header_block = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 Branch Social Listening Alert"
            }
        }
        
        # Create summary block
        summary_text = f"*Negative Sentiment Threshold Exceeded*\n"
        summary_text += f"• Negative Sentiment: *{negative_percentage:.1%}* (≥20% threshold)\n"
        summary_text += f"• Total Mentions Analyzed: {total_mentions}\n"
        summary_text += f"• Alert Time: {current_time}"
        
        summary_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": summary_text
            }
        }
        
        # Initialize blocks list
        message_blocks = [header_block, summary_block]
        
        # Add divider
        message_blocks.append({"type": "divider"})
        
        # Add top negative mentions
        if top_negative_mentions:
            mention_header = {
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"*Top {len(top_negative_mentions)} Most Negative Mentions:*"
                }
            }
            message_blocks.append(mention_header)
            
            for i, mention in enumerate(top_negative_mentions[:3], 1):
                # Extract mention details safely
                source = mention.get('source', 'unknown')
                user = mention.get('user', mention.get('username', 'unknown'))
                text = mention.get('text', mention.get('content', ''))
                sentiment_score = mention.get('sentiment_score', 0.0)
                url = mention.get('url', '')
                
                # Clean and truncate text for display
                if text:
                    clean_text = text.replace('\n', ' ').replace('\r', ' ').strip()
                    if len(clean_text) > 200:
                        clean_text = clean_text[:200] + "..."
                else:
                    clean_text = "No text available"
                
                # Format mention block
                mention_text = f"*{i}. {source.title()} - @{user}*\n"
                mention_text += f"Sentiment Score: {sentiment_score:.3f}\n"
                mention_text += f"_{clean_text}_"
                
                # Add URL if available
                if url:
                    mention_text += f"\n<{url}|View Original>"
                
                mention_block = {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": mention_text
                    }
                }
                
                message_blocks.append(mention_block)
        
        # Add footer
        footer_block = {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "🤖 Branch Social Listening Scraper | Powered by Hugging Face Sentiment Analysis"
                }
            ]
        }
        message_blocks.append(footer_block)
        
        # Create complete payload
        payload = {
            "blocks": message_blocks,
            "text": f"Branch Social Listening Alert: {negative_percentage:.1%} negative sentiment detected"
        }
        
        logging.info(f"✅ Formatted Slack message with {len(message_blocks)} blocks")
        return payload
        
    except Exception as e:
        logging.error(f"❌ Error formatting Slack message: {e}")
        
        # Fallback to simple text message
        fallback_payload = {
            "text": f"🚨 Branch Social Listening Alert: {negative_percentage:.1%} negative sentiment detected with {len(top_negative_mentions)} negative mentions. (Error formatting detailed message: {str(e)})"
        }
        
        return fallback_payload

def send_slack_alert(negative_percentage: float, top_negative_mentions: List[Dict[str, Any]], webhook_url: str = None, total_mentions: int = 0) -> bool:
    """
    Send Slack webhook message for negative sentiment alert
    
    Args:
        negative_percentage: Percentage of negative sentiment
        top_negative_mentions: Top negative mentions to include in alert
        webhook_url: Slack webhook URL (defaults to environment variable)
        total_mentions: Total number of mentions analyzed
        
    Returns:
        Boolean indicating success/failure
    """
    logging.info(f"🔔 Preparing to send Slack alert for {negative_percentage:.1%} negative sentiment")
    
    try:
        # Get webhook URL from environment if not provided
        if not webhook_url:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not webhook_url:
            logging.error("❌ No Slack webhook URL provided (check SLACK_WEBHOOK_URL environment variable)")
            return False
        
        # Validate webhook URL format
        if not webhook_url.startswith('https://hooks.slack.com/'):
            logging.error(f"❌ Invalid Slack webhook URL format: {webhook_url[:50]}...")
            return False
        
        # Format message payload
        payload = format_alert_message(negative_percentage, top_negative_mentions, total_mentions)
        
        if not payload:
            logging.error("❌ Failed to format Slack message payload")
            return False
        
        # Send webhook request
        logging.info(f"📤 Sending Slack webhook to: {webhook_url[:50]}...")
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Branch-Social-Listening-Scraper/1.0'
        }
        
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=30
        )
        
        # Check response status
        if response.status_code == 200:
            response_text = response.text.strip()
            if response_text == 'ok':
                logging.info("✅ Slack alert sent successfully")
                return True
            else:
                logging.error(f"❌ Slack webhook returned unexpected response: {response_text}")
                return False
        else:
            logging.error(f"❌ Slack webhook failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logging.error("❌ Slack webhook request timed out (30s)")
        return False
    except requests.exceptions.ConnectionError:
        logging.error("❌ Failed to connect to Slack webhook (network error)")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Slack webhook request failed: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Unexpected error sending Slack alert: {e}")
        logging.error(f"Error type: {type(e).__name__}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_slack_webhook(webhook_url: str = None) -> bool:
    """
    Test Slack webhook connection with a simple message
    
    Args:
        webhook_url: Slack webhook URL (defaults to environment variable)
        
    Returns:
        Boolean indicating if test was successful
    """
    logging.info("🧪 Testing Slack webhook connection...")
    
    try:
        # Get webhook URL from environment if not provided
        if not webhook_url:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not webhook_url:
            logging.error("❌ No Slack webhook URL provided for testing")
            return False
        
        # Create simple test message
        test_payload = {
            "text": "🧪 Branch Social Listening Scraper - Webhook Test",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🧪 Webhook Connection Test*\n✅ Branch Social Listening Scraper is configured correctly!"
                    }
                }
            ]
        }
        
        # Send test request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            webhook_url,
            data=json.dumps(test_payload),
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200 and response.text.strip() == 'ok':
            logging.info("✅ Slack webhook test successful")
            return True
        else:
            logging.error(f"❌ Slack webhook test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Slack webhook test failed: {e}")
        return False
