# Branch Social Listening Scraper MVP

A minimal end-to-end workflow that collects recent mentions of "Branch" from Twitter, Facebook, and Google Play, runs sentiment analysis, and logs results in Google Sheets with basic alerting for spikes in negative sentiment.

## 🎯 Demo Success Criteria

- Running `python run_all.py` locally fetches 50+ mentions across 3 sources
- Google Sheet shows new rows with proper sentiment analysis  
- Slack alert triggers when negative sentiment ≥20%
- GitHub Actions workflow runs successfully on schedule

## 🏗️ Project Structure

```
├── scrapers/
│   ├── twitter.py          # Twitter/X data collection via snscrape
│   ├── facebook.py         # Facebook posts/comments via facebook-scraper  
│   └── google_play.py      # Google Play reviews via google-play-scraper
├── analyze/
│   └── sentiment.py        # Sentiment analysis using Hugging Face transformers
├── store/
│   └── sheets.py           # Google Sheets integration via gspread
├── alerts/  
│   └── slack.py           # Slack webhook notifications
├── run_all.py             # Main orchestration script
├── requirements.txt       # Python dependencies
├── config_example.env     # Environment variables template
└── .github/workflows/
    └── run.yml           # GitHub Actions automation
```

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account (for Google Sheets API)
- Slack workspace with webhook permissions
- Git and GitHub account (for automation)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
4. Create service account credentials:
   - Go to "APIs & Services" > "Credentials"  
   - Click "Create Credentials" > "Service Account"
   - Fill in service account details and create
   - Click on the created service account
   - Go to "Keys" tab > "Add Key" > "Create New Key" > "JSON"
   - Download the JSON key file

5. Create Google Sheet:
   - Go to [Google Sheets](https://sheets.google.com/)
   - Create a new spreadsheet named "Branch Social Listening Data"
   - Share the sheet with your service account email (found in JSON file)
   - Give "Editor" permissions

### 3. Configure Slack Webhook

1. Go to your Slack workspace
2. Visit [Slack Apps](https://api.slack.com/apps) and click "Create New App"
3. Choose "From scratch" and select your workspace
4. Go to "Incoming Webhooks" and activate webhooks
5. Click "Add New Webhook to Workspace"
6. Choose the channel for notifications and authorize
7. Copy the webhook URL (starts with https://hooks.slack.com/services/)

### 4. Set Up Environment Variables

```bash
# Copy the example configuration
cp config_example.env .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

Fill in these required values:
```env
GOOGLE_SERVICE_ACCOUNT_FILE=/full/path/to/your/service-account-key.json
GOOGLE_SHEET_NAME=Branch Social Listening Data
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 5. Test Local Execution

```bash
# Run the complete pipeline
python run_all.py

# Check the logs
cat branch_scraper.log
```

Expected output:
- Console logs showing scraping progress
- New rows in your Google Sheet with sentiment data
- Slack notification if negative sentiment ≥20%

## 🤖 GitHub Actions Automation

### Quick Setup

1. **Push to GitHub** (if not already done):
   ```bash
   # Use the automated script
   ./push-to-github.sh
   
   # OR manually:
   git remote add origin https://github.com/USERNAME/REPO.git
   git branch -M main
   git push -u origin main
   ```

2. **Configure Secrets**: 
   📚 **[Follow the detailed GitHub Actions setup guide](GITHUB_ACTIONS_SETUP.md)** for complete step-by-step instructions.

3. **Required Secrets** (add in GitHub Settings → Secrets and variables → Actions):
   - `GOOGLE_SERVICE_ACCOUNT_FILE` - Your Google service account JSON
   - `GOOGLE_SHEET_NAME` - Name of your Google Sheet  
   - `SLACK_WEBHOOK_URL` - Your Slack webhook URL

4. **Test Workflow**:
   - Go to repository "Actions" tab
   - Click "Branch Social Listening Scraper" workflow
   - Click "Run workflow" to test manually

## 📊 Expected Data Format

Google Sheets will contain these columns:
- **timestamp**: When the data was collected
- **source**: twitter, facebook, or google_play  
- **id**: Unique identifier from source platform
- **user**: Username/author of the content
- **text**: The actual text content
- **sentiment_label**: positive, neutral, or negative
- **sentiment_score**: Confidence score (0-1)

## 🚨 Alerting Logic

Slack alerts trigger when:
- Negative sentiment percentage ≥ 20% in current run
- Alert includes top 3 most negative mentions
- Sent to configured Slack channel

## 🛠️ Tech Stack

- **Python 3.8+**: Core automation language
- **snscrape**: Twitter/X data collection  
- **facebook-scraper**: Facebook posts/comments
- **google-play-scraper**: Google Play app reviews
- **Hugging Face Transformers**: Sentiment analysis (`cardiffnlp/twitter-roberta-base-sentiment`)
- **gspread**: Google Sheets API integration
- **Slack Webhooks**: Notification delivery
- **GitHub Actions**: Automated scheduling

## 📝 Troubleshooting

### Common Issues

1. **Google Sheets Permission Denied**
   - Ensure service account email has Editor access to the sheet
   - Check that Google Sheets API is enabled in Cloud Console

2. **Slack Webhook 404 Error**
   - Verify webhook URL is correct and complete
   - Check that webhook is still active in Slack app settings

3. **Scraping Rate Limits**  
   - Twitter: Built-in delays, may need proxy rotation for heavy usage
   - Facebook: Respect rate limits, avoid excessive requests
   - Google Play: Usually more permissive, but monitor for blocks

4. **Sentiment Analysis Slow**
   - First run downloads ~1GB model, subsequent runs are faster
   - Consider using CPU vs GPU based on GitHub Actions constraints

5. **GitHub Actions Failures**
   - Check secrets are correctly configured
   - Review workflow logs in Actions tab
   - Verify all required environment variables are set

### Debug Mode

Add detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Resource Links

- [snscrape Documentation](https://github.com/JustAnotherArchivist/snscrape)
- [facebook-scraper Documentation](https://github.com/kevinzg/facebook-scraper)  
- [google-play-scraper Documentation](https://github.com/JoMingyu/google-play-scraper)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [gspread Documentation](https://docs.gspread.org/en/latest/)
- [GitHub Actions Cron Syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

## ⚖️ Legal & Ethical Considerations

- Respect platform Terms of Service and rate limits
- Only collect publicly available data
- Consider data privacy and storage implications
- Use for legitimate business/research purposes only

---

**Demo Focus**: This is an MVP designed for demonstration purposes. Production use would require additional error handling, monitoring, data validation, and compliance measures.
