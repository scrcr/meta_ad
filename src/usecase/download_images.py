from pathlib import Path
from typing import Dict, List

from src.core.ad import Ad
from src.interface.image_repository import ImageRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def download_images(repository: ImageRepository, ads: List[Ad], output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results: Dict[str, Path] = {}
    for ad in ads:
        logger.info("Downloading image for ad %s", ad.ad_id)
        image_path = repository.download(ad, output_dir)
        results[ad.ad_id] = image_path
        logger.debug("Saved image to %s", image_path)
    return results
