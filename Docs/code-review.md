## Code Review Log

This document records ongoing code and workflow reviews for the Branch Social Listening Scraper project. Each entry is a standalone section with date, topic, findings, and concrete action items. Add new entries to the top of the file.

---

### 2025-09-30 – Repository diff review: staged changes and demo criteria

**Scope**: `run_all.py`, `scrapers/twitter.py`, `scrapers/facebook.py`, `scrapers/google_play.py`, `scrapers/data_processor.py`, `collected_mentions.json`.

**Summary**
- Identified one blocker for CI (missing tracked module) and one logic issue that can fail the demo’s 50+ mentions requirement.

**Findings & Recommendations**
1) Missing module in VCS
   - Finding: `scrapers/data_processor.py` is untracked while imported by `run_all.py` → will raise `ModuleNotFoundError` in CI.
   - Recommendation: Add and commit `scrapers/data_processor.py`.

2) Twitter simulation caps at 10 items
   - Finding: `scrapers/twitter.py` generates at most the length of `sample_tweets` (10) even when `limit` is higher.
   - Recommendation: Iterate `for i in range(limit):` and index sample with modulo to produce up to `limit` items. Keep dedup by ID.

3) Demo success criteria (≥50 mentions)
   - Finding: Current collection targets: Twitter (10 simulated), Facebook (10), Google Play (25) ≈ 45 before dedup.
   - Recommendation: After fixing (2), set Twitter `limit` to 50; optionally bump Facebook `limit` in `run_all.py` from 10 → 20 to comfortably exceed 50 even after deduplication.

4) Credentials write robustness (non-blocking)
   - Finding: Workflow uses `echo` to write JSON secrets; special chars can be altered.
   - Recommendation: Prefer `printf '%s'` when writing `service_account.json`.

5) Dependency stability (non-blocking)
   - Finding: Broad `>=` specifiers may pull breaking releases over time.
   - Recommendation: Pin versions once a green build is achieved to stabilize CI.

**Action Items**
- [ ] Commit `scrapers/data_processor.py`
- [ ] Update Twitter simulation to generate up to `limit`
- [ ] Increase Facebook `limit` in `run_all.py` to 20
- [ ] Switch workflow secret write to `printf '%s'`
- [ ] Pin dependency versions after confirming a green run

---

### 2025-09-29 – CI/CD: GitHub Actions `run.yml` readiness review

**Scope**: `.github/workflows/run.yml`, dependency installation, secrets usage, logging/artifacts, and performance/cache considerations.

**References**:
- Deprecation notice for artifact actions v3 → [GitHub Changelog](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/)

**Summary**
- The workflow failed due to the deprecated `actions/upload-artifact@v3`. Updated to `@v4`, which resolves the immediate failure and aligns with GitHub’s deprecation policy (effective 2025-01-30).

**Findings & Recommendations**
1) Artifact action deprecation
   - Finding: `actions/upload-artifact@v3` is deprecated and causes automatic failures.
   - Resolution: Updated to `actions/upload-artifact@v4` (done).

2) Python 3.8 compatibility risk during dependency install
   - Finding: `requirements.txt` uses broad `>=` specifiers. Many libraries are ending Python 3.8 support; on `ubuntu-latest` this may fail to find wheels or compile.
   - Recommendation: Prefer `python-version: '3.10'` or pin versions compatible with 3.8.

3) Dependency pinning for stability
   - Finding: Broad `>=` can pull breaking major versions.
   - Recommendation: Pin minimal stable versions known to work on the runner to avoid flakiness. Example (adjust as validated):
     ```text
     snscrape==0.7.0
     facebook-scraper==0.2.59
     google-play-scraper==3.5.2
     torch==2.2.2
     transformers==4.38.*
     scipy==1.11.*
     gspread==6.0.*
     google-auth==2.29.*
     google-auth-oauthlib==1.2.*
     google-auth-httplib2==0.2.*
     requests==2.32.*
     python-dateutil==2.9.*
     pytz==2024.*
     ```

4) Google credential secret: content vs path
   - Finding: The workflow passes `GOOGLE_SERVICE_ACCOUNT_FILE` directly from a secret. If the secret stores JSON content (common), code expecting a file path will later fail.
   - Recommendation: Write the secret to a file on the runner, then export the path for downstream steps:
     ```yaml
     - name: Prepare Google service account file
       if: ${{ env.GOOGLE_SERVICE_ACCOUNT_FILE == '' }}
       run: |
         echo "${{ secrets.GOOGLE_SERVICE_ACCOUNT_FILE }}" > service_account.json
         echo "GOOGLE_SERVICE_ACCOUNT_FILE=$GITHUB_WORKSPACE/service_account.json" >> $GITHUB_ENV
     ```

5) Artifact upload when log file missing
   - Finding: If the job fails early, `branch_scraper.log` may be absent.
   - Recommendation: Guard with `if-no-files-found: ignore` to avoid step-level failures/warnings:
     ```yaml
     - name: Upload logs
       uses: actions/upload-artifact@v4
       if: always()
       with:
         name: scraper-logs
         path: branch_scraper.log
         retention-days: 30
         if-no-files-found: ignore
     ```

6) Action versions currency (prevent future deprecations)
   - Recommendation: Upgrade to `actions/setup-python@v5` and `actions/cache@v4` when convenient.

7) Model download performance & caching (future stage)
   - Finding: When sentiment analysis is implemented, first run downloads ~1GB from Hugging Face.
   - Recommendation: Cache the HF hub to reduce run time:
     ```yaml
     - name: Cache Hugging Face models
       uses: actions/cache@v4
       with:
         path: ~/.cache/huggingface/hub
         key: hf-${{ runner.os }}-${{ hashFiles('**/requirements.txt') }}-twitter-roberta-base-sentiment
         restore-keys: |
           hf-${{ runner.os }}-
     ```

8) Current app behavior (non-blocking now)
   - Observation: `run_all.py` primarily logs stage markers; scraping/analysis/storage are TODOs. The script exits non-zero only on exceptions, so CI will pass unless future implementations raise errors.

**Action Items**
- [x] Switch `actions/upload-artifact` to `@v4` (completed)
- [x] Bump Python to `3.10` (or pin 3.8-compatible versions) - COMPLETED: Updated to Python 3.10 for better compatibility
- [x] Add step to materialize Google credentials to a file - COMPLETED: Added step to write secret to file and set proper env var
- [x] Add `if-no-files-found: ignore` to artifact upload - COMPLETED: Prevents failures when log file doesn't exist
- [x] Upgrade `actions/setup-python@v5` and `actions/cache@v4` - COMPLETED: Updated to latest action versions
- [x] Add Hugging Face cache step before running the pipeline - COMPLETED: Added HF model caching to improve performance

---

### Template for Future Reviews

Use the following skeleton for new entries:

```
### YYYY-MM-DD – <Topic>

**Scope**: <files/areas>

**References**:
- <links>

**Summary**
- <short summary of findings and impact>

**Findings & Recommendations**
1) <finding>
   - Finding: <details>
   - Recommendation: <what to do>

**Action Items**
- [ ] <task 1>
- [ ] <task 2>
```


