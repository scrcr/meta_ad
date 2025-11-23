from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = (BASE_DIR / ".." / "output").resolve()
IMAGES_DIR = OUTPUT_DIR / "images"
DB_PATH = OUTPUT_DIR / "ads.sqlite"
RANKING_JSON = OUTPUT_DIR / "ranking.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
