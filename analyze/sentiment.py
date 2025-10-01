"""
Branch Social Listening Scraper - Sentiment Analysis Module
Uses Hugging Face model (cardiffnlp/twitter-roberta-base-sentiment) via transformers pipeline
Normalizes outputs into 3 classes: positive, neutral, negative
"""

import logging
from typing import List, Dict, Any, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Global sentiment analyzer instance (lazy loading)
_sentiment_analyzer = None

def get_sentiment_analyzer():
    """
    Get or create sentiment analysis pipeline using cardiffnlp/twitter-roberta-base-sentiment
    """
    global _sentiment_analyzer
    
    if _sentiment_analyzer is None:
        logging.info("Loading Hugging Face sentiment analysis model: cardiffnlp/twitter-roberta-base-sentiment")
        
        try:
            # Initialize the sentiment analysis pipeline
            model_name = "cardiffnlp/twitter-roberta-base-sentiment"
            
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Create pipeline
            _sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                return_all_scores=True
            )
            
            logging.info("✅ Sentiment analysis model loaded successfully")
            
        except Exception as e:
            logging.error(f"❌ Failed to load sentiment analysis model: {e}")
            raise
    
    return _sentiment_analyzer

def normalize_sentiment_label(label: str) -> str:
    """
    Normalize sentiment labels to standard format
    
    Args:
        label: Original sentiment label from model
        
    Returns:
        Normalized label: 'positive', 'neutral', or 'negative'
    """
    label_lower = label.lower()
    
    # Map cardiffnlp model labels to standard format
    if label_lower in ['label_2', 'positive']:
        return 'positive'
    elif label_lower in ['label_1', 'neutral']:
        return 'neutral'
    elif label_lower in ['label_0', 'negative']:
        return 'negative'
    else:
        # Default to neutral for unknown labels
        logging.warning(f"Unknown sentiment label: {label}, defaulting to neutral")
        return 'neutral'

def clean_text_for_sentiment(text: str) -> str:
    """
    Clean text for better sentiment analysis
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text string
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Basic text cleaning
    cleaned = text.strip()
    
    # Handle encoding issues
    try:
        cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        pass
    
    # Truncate very long texts (model has token limits)
    if len(cleaned) > 500:
        cleaned = cleaned[:500] + "..."
        
    return cleaned

def analyze_sentiment(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze sentiment of text list using Hugging Face transformers
    
    Args:
        texts: List of text strings to analyze
        
    Returns:
        List of dictionaries with sentiment labels and scores
    """
    logging.info(f"Starting sentiment analysis for {len(texts)} texts")
    
    if not texts:
        logging.warning("No texts provided for sentiment analysis")
        return []
    
    results = []
    
    try:
        # Get sentiment analyzer
        analyzer = get_sentiment_analyzer()
        
        # Clean texts
        cleaned_texts = [clean_text_for_sentiment(text) for text in texts]
        
        # Filter out empty texts
        valid_texts = [(i, text) for i, text in enumerate(cleaned_texts) if text.strip()]
        
        if not valid_texts:
            logging.warning("No valid texts after cleaning")
            return [{'sentiment_label': 'neutral', 'sentiment_score': 0.5, 'error': 'empty_text'} for _ in texts]
        
        # Run sentiment analysis on valid texts
        logging.info(f"Analyzing sentiment for {len(valid_texts)} valid texts")
        
        # Process texts in batches to avoid memory issues
        batch_size = 10
        analyzed_results = {}
        
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i+batch_size]
            batch_texts = [item[1] for item in batch]
            
            try:
                # Run analysis on batch
                predictions = analyzer(batch_texts)
                
                # Store results with original indices
                for j, (original_idx, _) in enumerate(batch):
                    pred_scores = predictions[j]
                    
                    # Find best prediction
                    best_pred = max(pred_scores, key=lambda x: x['score'])
                    
                    analyzed_results[original_idx] = {
                        'sentiment_label': normalize_sentiment_label(best_pred['label']),
                        'sentiment_score': round(best_pred['score'], 4),
                        'all_scores': {normalize_sentiment_label(p['label']): round(p['score'], 4) for p in pred_scores}
                    }
                    
            except Exception as e:
                logging.error(f"Error analyzing batch {i//batch_size + 1}: {e}")
                # Fill with neutral results for this batch
                for original_idx, _ in batch:
                    analyzed_results[original_idx] = {
                        'sentiment_label': 'neutral',
                        'sentiment_score': 0.5,
                        'error': f'analysis_failed: {str(e)}'
                    }
        
        # Create results list in original order
        for i, text in enumerate(texts):
            if i in analyzed_results:
                results.append(analyzed_results[i])
            else:
                # Text was filtered out during cleaning
                results.append({
                    'sentiment_label': 'neutral',
                    'sentiment_score': 0.5,
                    'error': 'invalid_text'
                })
        
        logging.info(f"✅ Sentiment analysis completed for {len(results)} texts")
        
        # Log sentiment distribution
        sentiment_counts = {}
        for result in results:
            label = result['sentiment_label']
            sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
        
        logging.info(f"📊 Sentiment distribution: {sentiment_counts}")
        
        return results
        
    except Exception as e:
        logging.error(f"❌ Sentiment analysis failed: {e}")
        # Return neutral results as fallback
        return [{'sentiment_label': 'neutral', 'sentiment_score': 0.5, 'error': f'failed: {str(e)}'} for _ in texts]

def calculate_sentiment_threshold(sentiment_results: List[Dict[str, Any]], threshold: float = 0.20) -> Tuple[bool, float, List[Dict[str, Any]]]:
    """
    Calculate if negative sentiment crosses threshold and return top negative mentions
    
    Args:
        sentiment_results: List of sentiment analysis results with combined mention data
        threshold: Negative sentiment threshold (default 20%)
        
    Returns:
        Tuple of (threshold_crossed, negative_percentage, top_negative_mentions)
    """
    logging.info(f"🎯 Calculating sentiment threshold with {len(sentiment_results)} mentions (threshold: {threshold:.1%})")
    
    if not sentiment_results:
        logging.warning("No sentiment results provided for threshold calculation")
        return False, 0.0, []
    
    try:
        # Count negative mentions and total valid mentions
        negative_mentions = []
        total_mentions = 0
        
        for mention in sentiment_results:
            # Skip mentions without proper sentiment analysis
            sentiment_label = mention.get('sentiment_label')
            sentiment_score = mention.get('sentiment_score')
            
            if sentiment_label and sentiment_score is not None:
                total_mentions += 1
                
                # Collect negative mentions
                if sentiment_label.lower() == 'negative':
                    negative_mentions.append(mention)
        
        if total_mentions == 0:
            logging.warning("No valid sentiment results found for threshold calculation")
            return False, 0.0, []
        
        # Calculate negative sentiment percentage
        negative_count = len(negative_mentions)
        negative_percentage = negative_count / total_mentions
        
        logging.info(f"📊 Sentiment analysis: {negative_count}/{total_mentions} negative ({negative_percentage:.1%})")
        
        # Check if threshold is crossed
        threshold_crossed = negative_percentage >= threshold
        
        if threshold_crossed:
            logging.warning(f"🚨 Negative sentiment threshold crossed: {negative_percentage:.1%} ≥ {threshold:.1%}")
            
            # Sort negative mentions by sentiment score (most negative first)
            sorted_negative = sorted(
                negative_mentions,
                key=lambda x: x.get('sentiment_score', 0.0),  # Lower score = more negative
                reverse=False  # Sort ascending (most negative first)
            )
            
            # Get top 3 negative mentions
            top_negative_mentions = sorted_negative[:3]
            
            logging.info(f"📋 Selected {len(top_negative_mentions)} top negative mentions for alert")
            
        else:
            logging.info(f"✅ Negative sentiment below threshold: {negative_percentage:.1%} < {threshold:.1%}")
            top_negative_mentions = []
        
        return threshold_crossed, negative_percentage, top_negative_mentions
        
    except Exception as e:
        logging.error(f"❌ Error calculating sentiment threshold: {e}")
        logging.error(f"Error type: {type(e).__name__}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False, 0.0, []
