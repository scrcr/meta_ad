from pathlib import Path
from typing import Dict, List

from src.core.ad import Ad
from src.interface.storage_repository import StorageRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def save_to_db(
    repository: StorageRepository,
    ads: List[Ad],
    image_paths: Dict[str, Path],
    ocr_results: Dict[str, str],
    tags: Dict[str, List[str]],
) -> None:
    for ad in ads:
        logger.info("Persisting ad %s", ad.ad_id)
        repository.store_ad(ad)
        repository.store_image(ad.ad_id, image_paths[ad.ad_id])
        repository.store_ocr(ad.ad_id, ocr_results.get(ad.ad_id, ""))
        repository.store_tags(ad.ad_id, tags.get(ad.ad_id, []))
    repository.commit()
    logger.info("All records persisted")
