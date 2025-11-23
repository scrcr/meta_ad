# Meta Ad Pipeline

Run the full offline Meta Ads analysis tool:

```bash
python -m src.main
```

The pipeline fetches sample ads, generates placeholder creatives, simulates OCR, derives image/layout/pitch tags, stores everything in SQLite under `output/ads.sqlite`, and writes a ranking report to `output/ranking.json`.
