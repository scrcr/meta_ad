# Meta Ads Processing Pipeline

## Overview
This project scrapes the Meta Ads Library web UI with Playwright using human-like pacing (random human Chrome user-agents, UK timezone/locale, persistent cookies, and slow scrolling) to collect creatives from major advertisers. Each run downloads creative snapshots, extracts on-image text with Tesseract OCR, performs lightweight CV analysis, generates concept tags, and optionally upserts new creatives into Supabase alongside a JSON ranking export.

Running `python -m src.main` will:
- Open Ads Library `view_all_page_id` pages for the configured advertisers and slowly scroll the feed to emulate a human user.
- Download creative snapshots immediately to `data/images/{ad_id}.jpg`.
- Preprocess images with OpenCV and run Tesseract OCR to capture embedded text.
- Analyze images for dominant HSV color, HaarCascade person detection, simple layout heuristics, and pitch classification.
- Generate concept tags from creative and OCR text, rank the ads, and export `output/ranking.json`.
- Optionally upsert normalized ad records into a Supabase `ads` table.

## Prerequisites
- Python 3.10+
- Playwright with Chromium (install via `python -m pip install playwright` then `python -m playwright install chromium`).
- System packages for OpenCV and Tesseract (e.g., `tesseract-ocr`, image codecs). Ensure `pytesseract` can find the `tesseract` binary on your PATH.
- Network access to Meta Ads Library (and Supabase if you want persistence).

## Setup
1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install playwright pillow imagehash opencv-python numpy pytesseract supabase python-dotenv
   python -m playwright install chromium
   ```
   Add any additional packages needed for your environment (e.g., `opencv-python-headless` for servers without GUI support).

2. **Configure environment**
   - Copy the sample and fill in values:
     ```bash
     cp env.sample .env
     ```
   - Export the variables (or use a tool like `direnv`/`dotenv`):
     ```bash
     export $(grep -v '^#' .env | xargs)
     ```

3. **Run the pipeline**
   ```bash
   python -m src.main
   ```
   The default pipeline scrapes a handful of watchlisted page IDs. Update the `SCRAPE_PAGE_IDS` env var or the `limit` argument in `src/usecase/run_pipeline.py` if you need a different volume.

## Configuration highlights
- **Watchlist**: `src/config.py` ships with a fixed set of 20 major-advertiser `SCRAPE_PAGE_IDS` (including Nike, Adidas, Amazon, and others). Override via the env var to target your own list.
- **Human pacing**: Scroll speed, viewport, locale, timezone, and user-agent rotation are configurable via `SCRAPER_*` env vars (see `env.sample`). Cookies/localStorage are persisted to `SCRAPER_STORAGE_STATE` to avoid repeated logins.
- **Supabase tables**: Ads upserts target `SUPABASE_TABLE` (default `ads`); page discovery is disabled in scraper mode but the `pages` table setting remains available for compatibility.

## Data flow and outputs
- **Images**: Saved under `data/images/{ad_id}.jpg`; directories are created automatically.
- **OCR + analysis**: Uses OpenCV preprocessing plus Tesseract OCR and image heuristics defined in `src/usecase/analyze_image.py`.
- **Tags**: Generated in `src/usecase/generate_tags.py` from creative and OCR text.
- **Persistence**: Supabase upsert is optional and controlled by credentials; normalized records flow through `src/infra/supabase_storage.py`.
- **Ranking export**: Final aggregation is written to `output/ranking.json` via `src/usecase/ranking.py`.

## Troubleshooting
- If Playwright cannot launch Chromium, re-run `python -m playwright install chromium` and verify sandboxing is allowed in your environment (use `SCRAPER_HEADLESS=false` for debugging).
- If Tesseract is not installed or images are unsupported, OCR will fail; verify the binary is available and images download correctly.
- Supabase writes are skipped when `SUPABASE_URL` or `SUPABASE_KEY` are unset, which is acceptable for local runs.
