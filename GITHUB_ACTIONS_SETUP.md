# 🚀 GitHub Actions Setup & Secrets Configuration Guide

## Step 1: Push Repository to GitHub

### 1.1 Create GitHub Repository
1. Go to [GitHub.com](https://github.com) and log in
2. Click the "+" icon in top right → "New repository"
3. Fill in repository details:
   - **Repository name**: `ai-scraper` or `branch-social-listening-scraper`
   - **Description**: `Branch Social Listening Scraper MVP - Automated sentiment analysis pipeline`
   - **Visibility**: Choose Private (recommended) or Public
   - **DO NOT** initialize with README, .gitignore, or license (we have these)
4. Click "Create repository"

### 1.2 Connect Local Repository to GitHub
```bash
# Add GitHub remote (replace with your username/repository)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Configure GitHub Secrets

### 2.1 Access Repository Secrets
1. Go to your GitHub repository
2. Click **"Settings"** tab (in the repository menu)
3. In left sidebar, click **"Secrets and variables"**
4. Click **"Actions"**
5. Click **"New repository secret"**

### 2.2 Add Required Secrets

#### Secret #1: Google Service Account JSON
- **Name**: `GOOGLE_SERVICE_ACCOUNT_FILE`
- **Value**: Copy the ENTIRE contents of your `your-project-id-123456-13efdda05630.json` file
  ```json
  {
    "type": "service_account",
    "project_id": "your-project-id-123456",
    "private_key_id": "your-private-key-id-here",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDPNVjBuCQYqY8K\nWd8WK/51vK0FZ4bl3z375CWaJBYro4A84NzeCC2vRdOvKgQy5cJEYoXcsxwi3YNE\nl70h2jbJD1dp0p74WKYe4/BaNlXyYNACdDu7TJ+GucRsqc8qsJ9CNUe+byO82L6J\n1FMl3V4iayh615i6qTnIgUDdbqd6zgBZpXu3j+HOGTDLkquF7AxNdwf06uiWmqCz\nn3VFku44DlFla6mE+frmRLLcUEOmnURMjAmP8G2FdLF3m97LaN1m9yDe886VwiTq\nGoUrOBodkp4pDY8fn0meShQoScDuSZKoZkBogEb7/OtfXGNbZUCkzGsuzAOZyWx2\nxM/8e9cnAgMBAAECggEAOFHCpxy6yu1DUMfup+MbTbsTuBVUiCRuf4maYtQOJpxR\nHbrsrXjBmhM7ny+nZoImlFnHEp6oNh3JMRqhMJNUMr/1vXCe/tdxh5Hi4VJFeBSy\nVQhst9LyxTa22eYpxeutzdwXfP5OU2UCHQpV80PA80/297Sj8ZBPgV0IWWdbJDhe\ndhIA3EM6guOZtJPPKviKj4HjiaTCjgN2g3FxhK+dD2jPoMrYdG8u0Ko/ToS8+ZIn\nh5eG6PEizW32a5N+jLjPljsq50R2HEJ/AYiPXcMcNGJ2TNBR1AausPUSiOh7mfBZ\n2GuFgDEhHkV7RK+SKj+nT29BX6YRdKE67HznWH9AWQKBgQDwMONUxFpQrUerzhY5\nY5BrOIPcu9eVBKRsLXvt7fblMOyb8yG5FXXpLZal32x4BksObxG6WmMDoyRBLxKo\nHQHG8IsxBO5qRBwbXnGsixmfrbFNO0hNqdVuhJZhUmGsTWAAVvjhruAy3YGJxEGh\ncJRXkMLT+hfUlmOUkfOQts7PkwKBgQDc2Ld5oCeolLHHU5t2l7D1r7IuHkwMSmfY\n/jpWO5yke/0IN78ttjbysgoScCJrYC3dBiX8BSJSF04vNzgzEiZ4C23cW4vgDCOg\nURoRB3GII+5xHfa2mPLC47nUAV2ljzFnTrD9O5ejVwZ5u7dATZRtUuPwpCm9wW/h\njjePeVGOnQKBgQDAtSifaQ5hLjWTpTx1fOlw7R32qosT126oEHIe+k6dofwkPxSu\nb4ZzuAznNnPLdJkhkoFxt3U7hNfgqIjacrNrTrEOejti7RRz7PldCxla4LuhEFA5\nZ2qDSkNw/+y3ljjQ7Pav82OTy95Tjy9s/Gs4Oj/mXQBjoulwWQ1G7TTOmwKBgQCw\nGxCTqCZ3w7rQG9eIhgXSpLwNEpPJ6TtOScvzH64Va9mmR+3nYboHZfmqIkkQHq3z\n5gc8JEvt8i+ibwIdl4edil+crFOp4YQ3PvTuR2U9DooBIceua+CJkFaKvFwUvU7D\n9ngkNvUAh1DemdXTLQoC82pYZk/yxOGWl3Wurytd8QKBgQCRYMSuNJRszwRgo1gV\nf8sTLtwJfTbSvtFrSaelqoaAfdDS9pkKcO17BUVHH4qzRyhI8JjAtyPA3Mr6uNf2\nere9rsAD/PIx7DXSyLEKZ16Wn9DP1viv3dD35psuZDAk80KMEG0uIKOqISiSqT/p\na9nb85iQMMkRtCk3vvrrNAmN6A==\n-----END PRIVATE KEY-----\n",
    "client_email": "branch-scraper@your-project-id-123456.iam.gserviceaccount.com",
    "client_id": "123456789012345678901",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/branch-scraper%40your-project-id-123456.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
  }
  ```
- Click **"Add secret"**

#### Secret #2: Google Sheet Name
- **Name**: `GOOGLE_SHEET_NAME`
- **Value**: `Branch Social Listening Data`
- Click **"Add secret"**

#### Secret #3: Slack Webhook URL
- **Name**: `SLACK_WEBHOOK_URL`
- **Value**: `https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK`
  
  📝 **To get your Slack webhook URL:**
  1. Go to [Slack API Apps](https://api.slack.com/apps)
  2. Click "Create New App" → "From scratch"
  3. Enter app name: `Branch Social Listening Alerts`
  4. Select your workspace
  5. Go to "Incoming Webhooks" → Turn on "Activate Incoming Webhooks"
  6. Click "Add New Webhook to Workspace"
  7. Select channel (e.g., #general or #alerts)
  8. Copy the webhook URL
- Click **"Add secret"**

### 2.3 Optional Configuration Secrets

These have default values but can be customized:

#### Optional Secret #4: Twitter Query
- **Name**: `TWITTER_QUERY`
- **Value**: `Branch OR @BranchApp` (default)
- Customize to search different terms

#### Optional Secret #5: Facebook Page
- **Name**: `FACEBOOK_PAGE`
- **Value**: `Branch` (default)
- Customize to monitor different Facebook pages

#### Optional Secret #6: Google Play App ID
- **Name**: `GOOGLE_PLAY_APP_ID`
- **Value**: `io.branch.referral.branch` (default)
- Customize to monitor different Android apps

#### Optional Secret #7: Sentiment Threshold
- **Name**: `NEGATIVE_SENTIMENT_THRESHOLD`
- **Value**: `0.20` (20% threshold)
- Customize alert sensitivity (0.1 = 10%, 0.3 = 30%, etc.)

## Step 3: Verify GitHub Actions Workflow

### 3.1 Check Workflow File
Your workflow file is already created at `.github/workflows/run.yml`. It should contain:

```yaml
name: Branch Social Listening Scraper

on:
  # Run daily at 9 AM UTC
  schedule:
    - cron: '0 9 * * *'
  
  # Allow manual trigger
  workflow_dispatch:

jobs:
  scrape-and-analyze:
    runs-on: ubuntu-latest
    # ... rest of workflow
```

### 3.2 View Workflows in GitHub
1. Go to your repository
2. Click **"Actions"** tab
3. You should see "Branch Social Listening Scraper" workflow listed

## Step 4: Test the Workflow

### 4.1 Manual Test Run
1. In GitHub repository, go to **"Actions"** tab
2. Click on "Branch Social Listening Scraper" workflow
3. Click **"Run workflow"** button (on right side)
4. Click green **"Run workflow"** button to confirm
5. Wait for workflow to start (may take a few seconds)

### 4.2 Monitor Workflow Execution
1. Click on the running workflow to view details
2. Click on the "scrape-and-analyze" job
3. Watch real-time logs in each step:
   - "Checkout repository"
   - "Set up Python 3.8+"
   - "Install dependencies"
   - "Run Branch Social Listening Scraper"

### 4.3 Expected Results
✅ **Success indicators:**
- All steps show green checkmarks
- Python dependencies install successfully
- Script runs without errors
- Logs show "Branch Social Listening Scraper MVP Started"

⚠️ **Current limitations (until Stage 2):**
- Scrapers will return empty results (placeholder functions)
- No data will be written to Google Sheets yet
- No Slack alerts will be sent yet

## Step 5: Troubleshooting Common Issues

### Issue 1: Workflow Permission Denied
**Error**: `Error: Process completed with exit code 1`

**Solution:**
1. Go to repository **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select **"Read and write permissions"**
3. Click **"Save"**

### Issue 2: Google Sheets Authentication Failed
**Error**: `google.auth.exceptions.DefaultCredentialsError`

**Solution:**
1. Verify `GOOGLE_SERVICE_ACCOUNT_FILE` secret contains valid JSON
2. Ensure service account email has access to the Google Sheet
3. Check that Google Sheets API is enabled in Google Cloud Console

### Issue 3: Slack Webhook 404 Error
**Error**: `404 Client Error: Not Found`

**Solution:**
1. Verify webhook URL is complete and correct
2. Test webhook manually with curl:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
   --data '{"text":"Test message"}' \
   YOUR_WEBHOOK_URL
   ```
3. Regenerate webhook if necessary

### Issue 4: Python Dependencies Failed
**Error**: Package installation failures

**Solution:**
1. Check `requirements.txt` for typos
2. Pin specific versions if conflicts occur
3. Review workflow logs for specific error details

### Issue 5: Workflow Not Triggering on Schedule
**Problem**: Workflow doesn't run daily

**Solution:**
1. Ensure repository has recent activity (GitHub may disable inactive workflows)
2. Commit a small change to keep repository active
3. Manual triggers always work regardless of schedule

## Step 6: Monitoring & Maintenance

### 6.1 Workflow Status Monitoring
- GitHub will email you if workflows fail
- Check **Actions** tab regularly for status
- Review workflow logs for any warnings

### 6.2 Security Best Practices
- ✅ Never commit credentials to git
- ✅ Use GitHub secrets for sensitive data
- ✅ Regularly rotate Slack webhooks and Google service accounts
- ✅ Monitor repository access and permissions

### 6.3 Schedule Customization
Modify cron schedule in `.github/workflows/run.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'    # Daily at 9 AM UTC
  - cron: '0 */6 * * *'  # Every 6 hours  
  - cron: '0 0 * * 1'    # Weekly on Monday
  - cron: '0 0 1 * *'    # Monthly on 1st
```

Use [crontab.guru](https://crontab.guru/) to test cron expressions.

## Next Steps

Once your GitHub Actions is configured and running:

1. ✅ **Stage 1 Complete**: Environment & automation setup
2. 🚧 **Stage 2 Next**: Implement actual scraping functionality
3. 🚧 **Stage 3 Next**: Add sentiment analysis and Google Sheets storage
4. 🚧 **Stage 4 Next**: Complete alerting and testing

---

## 📋 Quick Checklist

- [ ] Repository pushed to GitHub
- [ ] `GOOGLE_SERVICE_ACCOUNT_FILE` secret added
- [ ] `GOOGLE_SHEET_NAME` secret added  
- [ ] `SLACK_WEBHOOK_URL` secret added
- [ ] Optional configuration secrets added (if desired)
- [ ] Manual workflow test completed successfully
- [ ] Google Sheet created and shared with service account
- [ ] Slack webhook tested and working
- [ ] Schedule configured for daily runs

**🎉 Congratulations!** Your GitHub Actions automation is now set up and ready for the scraping implementation in Stage 2!
