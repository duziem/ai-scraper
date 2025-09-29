# **Product Requirements Document (PRD)**

**Project:** Social Listening MVP for Branch  
 **Goal:** Build a minimal end-to-end workflow that collects recent mentions of “Branch” from Twitter, Facebook, and Google Play, runs sentiment analysis, and logs results in Google Sheets. Includes basic alerting for spikes in negative sentiment.

---

## **1\. Objective**

Demonstrate an automated pipeline that:

1. Fetches **recent mentions/reviews** from 3 sources: Twitter, Facebook, Google Play.

2. Runs **sentiment analysis** on each text.

3. Logs results (text \+ source \+ sentiment) in **Google Sheets**.

4. Triggers a **Slack alert** if negative sentiment crosses a threshold.

This MVP is for a **demo only** — minimal reliability required, but should handle common errors gracefully.

---

## **2\. Scope (MVP Features)**

* **Twitter (X):** Scrape latest tweets containing `"Branch OR @BranchApp"` using `snscrape`.

* **Facebook:** Scrape posts/comments from the public Branch Facebook page using `facebook-scraper`.

* **Google Play:** Fetch \~100 most recent reviews using `google-play-scraper`.

* **Sentiment Analysis:** Use Hugging Face model (`cardiffnlp/twitter-roberta-base-sentiment`) via `transformers` pipeline.

* **Storage:** Append structured results into a Google Sheet (via `gspread` and a service account).

* **Alerting:** If % negative ≥ 20% in last run, send Slack webhook message with top 3 negative texts.

---

## **3\. Out of Scope**

* No full database or persistent history beyond Google Sheets.

* No advanced NLP (topics, clustering, multilingual).

* No retries/robust job queue.

* No advanced monitoring — just print logs to console.

---

## **4\. Architecture (Minimal Flow)**

GitHub Actions (cron)  
   ↓  
Python scrapers (snscrape, facebook-scraper, google-play-scraper)  
   ↓  
Sentiment analysis (Hugging Face transformers pipeline)  
   ↓  
Google Sheets (append results)  
   ↓  
Slack webhook (alert if negative threshold crossed)

---

## **5\. Implementation Requirements**

### **5.1 Scrapers**

* **Twitter:**

  * Tool: [snscrape](https://github.com/JustAnotherArchivist/snscrape)

  * Usage: Fetch last \~100 tweets. Deduplicate by tweet ID.

* **Facebook:**

  * Tool: [facebook-scraper](https://github.com/kevinzg/facebook-scraper)

  * Usage: Fetch \~20 latest posts/comments from the Branch page.

* **Google Play:**

  * Tool: [google-play-scraper (Python)](https://github.com/JoMingyu/google-play-scraper)

  * Usage: Fetch \~100 newest reviews of Branch app.

### **5.2 Sentiment Analysis**

* **Library:** [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)

* **Model:** [cardiffnlp/twitter-roberta-base-sentiment](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment)

* Normalize outputs into 3 classes: `positive`, `neutral`, `negative`.

### **5.3 Storage**

* **Library:** [gspread](https://docs.gspread.org/en/latest/) for Google Sheets API.

* Each row \= `{timestamp, source, id, user, text, sentiment_label, sentiment_score}`.

### **5.4 Alerting**

* **Slack Webhook:** [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

* If ≥20% negative, post summary with top 3 negative texts.

### **5.5 Scheduling**

* **GitHub Actions:** [GitHub Actions cron syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)

* Run once per day (or manual trigger).

---

## **6\. Pitfall Handling**

* **Rate limits / scraping errors:** Catch exceptions, log warning, skip gracefully.

* **Malformed text / encoding:** Ensure `.encode("utf-8", errors="ignore")`.

* **Empty batch (e.g., no posts found):** Log “no data” instead of crashing.

* **Google Sheets auth failure:** Check for missing credentials, print meaningful error.

---

## **7\. Deliverables**

**Repo structure**:

 /scrapers/twitter.py  
/scrapers/facebook.py  
/scrapers/google\_play.py  
/analyze/sentiment.py  
/store/sheets.py  
/alerts/slack.py  
run\_all.py  
.github/workflows/run.yml  
README.md

1. **README.md**: Instructions for setting up Google service account, Slack webhook, running locally, and GitHub Actions setup.

---

## **8\. Demo Success Criteria**

* Running `python run_all.py` locally fetches \~50+ mentions across 3 sources.

* Google Sheet shows rows with sentiment.

* If ≥20% mentions are negative, a Slack message posts.

---

## **9\. Future Extensions (not required now)**

* Add database (Postgres/Supabase) for historical data.

* Advanced NLP (topic extraction, aspect classification).

* Dashboards (Looker Studio or Streamlit).

---

**End of PRD**

