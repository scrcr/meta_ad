import json
from pathlib import Path
from typing import List

from src import config
from src.core.ad import Ad
from src.infra.file_downloader import FileDownloader
from src.infra.meta_api import MetaAdsApiClient
from src.infra.sqlite_storage import SQLiteStorage
from src.infra.tesseract_engine import SimpleTesseractEngine
from src.usecase.analyze_image import analyze_images
from src.usecase.download_images import download_images
from src.usecase.fetch_ads import fetch_ads
from src.usecase.generate_tags import generate_tags
from src.usecase.ocr_text import ocr_text
from src.usecase.save_to_db import save_to_db
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _ensure_output_dirs() -> None:
    Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.IMAGES_DIR).mkdir(parents=True, exist_ok=True)


def _build_dependencies():
    ads_repo = MetaAdsApiClient()
    image_repo = FileDownloader()
    ocr_engine = SimpleTesseractEngine()
    storage = SQLiteStorage(Path(config.DB_PATH))
    return ads_repo, image_repo, ocr_engine, storage


def _rank_tags(storage: SQLiteStorage) -> List[dict]:
    return storage.fetch_tag_ranking()


def _export_ranking(ranking: List[dict]) -> None:
    Path(config.RANKING_JSON).write_text(json.dumps(ranking, ensure_ascii=False, indent=2))


def run() -> None:
    _ensure_output_dirs()
    ads_repo, image_repo, ocr_engine, storage = _build_dependencies()

    ads: List[Ad] = fetch_ads(ads_repo)
    image_paths = download_images(image_repo, ads, Path(config.IMAGES_DIR))
    ocr_results = ocr_text(ocr_engine, image_paths)
    image_descriptions = analyze_images(image_paths, ocr_results)
    tag_map = generate_tags(image_descriptions, ocr_results)
    save_to_db(storage, ads, image_paths, ocr_results, tag_map)

    ranking = _rank_tags(storage)
    logger.info("Tag ranking: %s", ranking)
    _export_ranking(ranking)
    print(json.dumps(ranking, ensure_ascii=False, indent=2))


__all__ = ["run"]
