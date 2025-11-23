# Meta Ads Processing Pipeline

## Overview
This project provides an end-to-end pipeline for collecting Meta ads, downloading their creative snapshots, extracting on-image text with Tesseract OCR, performing lightweight computer-vision analysis, generating conceptual tags, and persisting results to Supabase alongside a JSON ranking export.

Running `python -m src.main` will:
- Fetch ads from the Meta Graph API using both Guarantee and Explore delivery modes with pagination.
- Download creative snapshots immediately to `data/images/{ad_id}.jpg`.
- Preprocess images with OpenCV and run Tesseract OCR to capture embedded text.
- Analyze images for dominant HSV color, HaarCascade person detection, simple layout heuristics, and pitch classification.
- Generate concept tags from creative and OCR text, rank the ads, and export `output/ranking.json`.
- Optionally upsert normalized ad records into a Supabase `ads` table.

## Prerequisites
- Python 3.10+
- System packages for OpenCV and Tesseract (e.g., `tesseract-ocr`, image codecs). Ensure `pytesseract` can find the `tesseract` binary on your PATH.
- Network access to the Meta Graph API and (optionally) Supabase.

## Setup
1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install requests opencv-python numpy pytesseract
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
   The default pipeline fetches 10 ads (split across modes inside the use case). Update the `limit` argument in `src/usecase/run_pipeline.py` or in your own entrypoint invocation if you need a different volume.

## Configuration highlights
- **Guarantee watchlist**: `src/config.py` ships with a fixed set of 20 major-advertiser `GUARANTEE_PAGE_IDS` (including Nike, Adidas, Amazon, and others). You can override by setting the `GUARANTEE_PAGE_IDS` env var (comma-separated). Guarantee requests include `ad_reached_countries=GB` and paginate until `paging.next` is exhausted.
- **Explore discovery**: The Explore mode cycles through `SEARCH_TERMS` (default: `the,a,to,for,in`) to uncover new `page_id`s. Unique discoveries are persisted to Supabase via the `pages` table (configurable with `SUPABASE_PAGE_TABLE`).
- **Supabase tables**: Ads upserts target `SUPABASE_TABLE` (default `ads`); page discovery upserts target `SUPABASE_PAGE_TABLE` (default `pages`).

## Data flow and outputs
- **Images**: Saved under `data/images/{ad_id}.jpg`; directories are created automatically.
- **OCR + analysis**: Uses OpenCV preprocessing plus Tesseract OCR and image heuristics defined in `src/usecase/analyze_image.py`.
- **Tags**: Generated in `src/usecase/generate_tags.py` from creative and OCR text.
- **Persistence**: Supabase upsert is optional and controlled by credentials; normalized records flow through `src/infra/supabase_storage.py`.
- **Ranking export**: Final aggregation is written to `output/ranking.json` via `src/usecase/ranking.py`.

## Troubleshooting
- Missing Meta credentials will cause fetch failures; ensure `META_ACCESS_TOKEN` and `META_ACCOUNT_ID` are set.
- If Tesseract is not installed or images are unsupported, OCR will fail; verify the binary is available and images download correctly.
- Supabase writes are skipped when `SUPABASE_URL` or `SUPABASE_KEY` are unset, which is acceptable for local runs.

