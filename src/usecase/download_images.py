import os
from typing import Iterable, List

from src.core.ad import Ad
from src.interface.image_repository import ImageRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def download_ad_images(image_repo: ImageRepository, ads: Iterable[Ad], base_dir: str) -> List[Ad]:
    updated: List[Ad] = []
    for ad in ads:
        filename = f"{ad.ad_id}.jpg"
        dest_path = os.path.join(base_dir, filename)
        try:
            ad.image_path = image_repo.download(ad.snapshot_url, dest_path)
            logger.debug("Downloaded ad %s to %s", ad.ad_id, ad.image_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to download ad %s: %s", ad.ad_id, exc)
            ad.image_path = None
        updated.append(ad)
    return updated
