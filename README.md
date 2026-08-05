# RSE Trading Dashboard  (June 2026)

An interactive Streamlit dashboard analyzing Rwanda Stock Exchange trading data for June 2026.

## Files
- `app.py` — the dashboard
- `rse_june2026_clean.csv` — cleaned dataset (must sit in the same folder as `app.py`)
- `requirements.txt` — dependencies

## What was cleaned from the raw file
- Removed a totals/summary row and blank rows with no date or security.
- Fixed two broker-code typos: `B10` → `BR10`, `BRK10` → `BR10`.
- Added an `Asset Type` column (Equity vs Bond, detected from security codes) and a
  human-readable `Security Name` column.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the local URL Streamlit prints (usually http://localhost:8501).

## Deploy on Streamlit Community Cloud (free)
1. Create a **public GitHub repo** (or a private one — Streamlit Cloud can access private
   repos once you connect your GitHub account) and push these three files:
   `app.py`, `rse_june2026_clean.csv`, `requirements.txt`.
2. Go to **https://share.streamlit.io** and sign in with GitHub.
3. Click **"New app"**, pick your repo/branch, and set the main file path to `app.py`.
4. Click **Deploy**. First build takes 1–3 minutes.
5. Any time you push new commits to the repo, the deployed app updates automatically.

### Common deployment pitfalls this app already avoids
- **Missing data file**: the CSV is loaded with a relative path (`rse_june2026_clean.csv`),
  so as long as it's in the repo root next to `app.py`, it will be found on Streamlit Cloud.
- **Version mismatches**: `requirements.txt` pins minimum compatible versions.
- **Large repo files**: the CSV is small (~185 rows), so there's no size-limit risk.
- **Caching**: `@st.cache_data` on the loader keeps reloads fast without re-reading the file
  on every filter change.

## Updating with new months of data
To extend this to more than June 2026, append new cleaned rows to
`rse_june2026_clean.csv` (or point `load_data()` at multiple files and `pd.concat` them) —
every chart and KPI will pick up the new dates automatically since they're all computed from
the filtered dataframe, not hardcoded.
