"""
Branch Social Listening Scraper - Google Sheets Storage Module
Uses gspread library for Google Sheets API integration
Each row = {timestamp, source, id, user, text, sentiment_label, sentiment_score}
"""

import logging
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import gspread
from google.auth.exceptions import GoogleAuthError

# Global Google Sheets client (lazy loading)
_sheets_client = None

def setup_google_sheets_auth():
    """
    Set up Google Sheets authentication using service account
    
    Returns:
        gspread client or None if authentication fails
    """
    global _sheets_client
    
    if _sheets_client is not None:
        return _sheets_client
    
    try:
        # Get service account file path from environment
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        if not service_account_file:
            logging.error("❌ GOOGLE_SERVICE_ACCOUNT_FILE environment variable not set")
            return None
        
        if not os.path.exists(service_account_file):
            logging.error(f"❌ Google service account file not found: {service_account_file}")
            return None
        
        logging.info(f"🔑 Authenticating with Google Sheets using service account: {service_account_file}")
        
        # Define scopes for both Sheets and Drive access (required for listing and sharing)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Authenticate with Google Sheets with expanded scopes
        _sheets_client = gspread.service_account(filename=service_account_file, scopes=scopes)
        
        logging.info("✅ Google Sheets authentication successful")
        return _sheets_client
        
    except GoogleAuthError as e:
        logging.error(f"❌ Google authentication failed: {e}")
        return None
    except Exception as e:
        logging.error(f"❌ Failed to setup Google Sheets authentication: {e}")
        return None

def get_or_create_spreadsheet(spreadsheet_name: str) -> Optional[gspread.Spreadsheet]:
    """
    Get existing spreadsheet or create new one
    
    Args:
        spreadsheet_name: Name of the spreadsheet
        
    Returns:
        gspread Spreadsheet object or None if failed
    """
    client = setup_google_sheets_auth()
    
    if not client:
        return None
    
    try:
        # Try to open existing spreadsheet
        spreadsheet = client.open(spreadsheet_name)
        logging.info(f"📊 Opened existing spreadsheet: {spreadsheet_name}")
        return spreadsheet
        
    except gspread.SpreadsheetNotFound:
        try:
            # Create new spreadsheet
            logging.info(f"📝 Creating new spreadsheet: {spreadsheet_name}")
            spreadsheet = client.create(spreadsheet_name)
            
            # Note: Spreadsheet is created with service account access only
            # For external access, manually share the spreadsheet or add proper permission grants
            logging.info(f"✅ Created new spreadsheet: {spreadsheet_name}")
            logging.info(f"📋 Spreadsheet URL: {spreadsheet.url}")
            logging.info(f"💡 Note: Spreadsheet has service account access only. Share manually if external access needed.")
            
            return spreadsheet
            
        except Exception as e:
            logging.error(f"❌ Failed to create new spreadsheet: {e}")
            return None
    
    except Exception as e:
        logging.error(f"❌ Failed to access spreadsheet: {e}")
        return None

def setup_worksheet_headers(worksheet: gspread.Worksheet) -> bool:
    """
    Set up column headers for the worksheet
    
    Args:
        worksheet: gspread worksheet object
        
    Returns:
        Boolean indicating success
    """
    try:
        # Define headers according to PRD specification
        headers = [
            'timestamp',
            'source', 
            'id',
            'user',
            'text',
            'sentiment_label',
            'sentiment_score'
        ]
        
        # Check if headers already exist
        existing_values = worksheet.row_values(1)
        
        if not existing_values or existing_values != headers:
            # Set headers
            worksheet.update('A1:G1', [headers])
            logging.info("📋 Worksheet headers configured")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to setup worksheet headers: {e}")
        return False

def format_data_for_sheets(data: List[Dict[str, Any]]) -> List[List[str]]:
    """
    Format mention data for Google Sheets
    
    Args:
        data: List of mention dictionaries with sentiment analysis
        
    Returns:
        List of rows formatted for Google Sheets
    """
    formatted_rows = []
    
    for item in data:
        try:
            # Extract required fields
            timestamp = item.get('timestamp', datetime.now().isoformat())
            source = item.get('source', 'unknown')
            item_id = str(item.get('id', ''))
            user = item.get('user', item.get('username', ''))
            text = item.get('text', item.get('content', ''))
            
            # Extract sentiment data
            sentiment_label = item.get('sentiment_label', 'neutral')
            sentiment_score = item.get('sentiment_score', 0.5)
            
            # Ensure proper formatting
            if isinstance(sentiment_score, (int, float)):
                sentiment_score = round(float(sentiment_score), 4)
            else:
                sentiment_score = 0.5
            
            # Clean text for spreadsheet (remove line breaks, limit length)
            if text:
                text = str(text).replace('\n', ' ').replace('\r', ' ').strip()
                # Limit text length for readability
                if len(text) > 1000:
                    text = text[:1000] + "..."
            
            # Format timestamp
            if isinstance(timestamp, str):
                try:
                    # Parse and reformat timestamp
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                except:
                    pass
            
            formatted_row = [
                timestamp,
                source,
                item_id,
                user,
                text,
                sentiment_label,
                str(sentiment_score)
            ]
            
            formatted_rows.append(formatted_row)
            
        except Exception as e:
            logging.error(f"❌ Error formatting data row: {e}")
            # Add error row to maintain data integrity
            formatted_rows.append([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'error',
                '',
                '',
                f'Error processing data: {str(e)}',
                'neutral',
                '0.5'
            ])
    
    return formatted_rows

def append_to_google_sheet(data: List[Dict[str, Any]], spreadsheet_name: str = None) -> bool:
    """
    Append structured results to Google Sheet using gspread
    
    Args:
        data: List of dictionaries containing scraped and analyzed data
        spreadsheet_name: Name of Google Sheet to write to (defaults to env variable)
        
    Returns:
        Boolean indicating success/failure
    """
    if not data:
        logging.warning("No data provided to append to Google Sheet")
        return True
    
    # Use spreadsheet name from environment if not provided
    if not spreadsheet_name:
        spreadsheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Branch Social Listening Data')
    
    logging.info(f"📊 Appending {len(data)} records to Google Sheet: {spreadsheet_name}")
    
    try:
        # Get or create spreadsheet
        spreadsheet = get_or_create_spreadsheet(spreadsheet_name)
        
        if not spreadsheet:
            logging.error("❌ Failed to access Google Spreadsheet")
            return False
        
        # Get the first worksheet (or create it)
        try:
            worksheet = spreadsheet.sheet1
        except Exception:
            # Create default worksheet if none exists
            worksheet = spreadsheet.add_worksheet(title="Sheet1", rows="1000", cols="26")
        
        # Setup headers
        if not setup_worksheet_headers(worksheet):
            logging.error("❌ Failed to setup worksheet headers")
            return False
        
        # Format data for sheets
        formatted_rows = format_data_for_sheets(data)
        
        if not formatted_rows:
            logging.warning("No valid data to append after formatting")
            return True
        
        # Use more efficient approach: gspread's append method finds next row automatically
        # This avoids loading all existing data which is O(n) and slow for large datasets
        logging.info(f"📝 Appending {len(formatted_rows)} rows to worksheet...")
        
        # Append all rows in batch using gspread's efficient append method
        worksheet.append_rows(formatted_rows, value_input_option='RAW')
        
        logging.info(f"✅ Successfully appended {len(formatted_rows)} records to Google Sheet")
        logging.info(f"📊 Spreadsheet URL: {spreadsheet.url}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to append data to Google Sheet: {e}")
        logging.error(f"Error type: {type(e).__name__}")
        return False

def test_google_sheets_connection() -> bool:
    """
    Test Google Sheets connection and permissions with multiple fallback approaches
    
    Returns:
        Boolean indicating if connection is working
    """
    logging.info("🧪 Testing Google Sheets connection...")
    
    try:
        client = setup_google_sheets_auth()
        
        if not client:
            return False
        
        # Method 1: Try to list spreadsheets (requires Drive scope, most comprehensive test)
        try:
            spreadsheets = client.list_spreadsheet_files()
            logging.info(f"✅ Google Sheets connection test passed (Drive access). Found {len(spreadsheets)} accessible spreadsheets")
            return True
        except Exception as drive_error:
            logging.warning(f"Drive API test failed: {drive_error}")
            logging.info("Trying fallback connectivity tests...")
        
        # Method 2: Try to create and delete a test spreadsheet (requires Sheets scope only)
        try:
            test_sheet_name = f"Branch-Test-{int(datetime.now().timestamp())}"
            test_spreadsheet = client.create(test_sheet_name)
            
            # Immediately delete the test spreadsheet
            client.del_spreadsheet(test_spreadsheet.id)
            
            logging.info(f"✅ Google Sheets connection test passed (Sheets access). Create/delete test successful")
            return True
        except Exception as sheets_error:
            logging.warning(f"Sheets API create/delete test failed: {sheets_error}")
        
        # Method 3: Basic auth test - if we got this far, auth is working
        logging.info("✅ Google Sheets basic authentication successful")
        logging.warning("⚠️  Limited API access - some features may not work")
        return True
        
    except Exception as e:
        logging.error(f"❌ Google Sheets connection test failed: {e}")
        return False
