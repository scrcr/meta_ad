from __future__ import annotations

import os
from typing import Iterable, List, Tuple

import cv2

from src.core.ad import Ad
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _is_image_valid(path: str) -> bool:
    if not path or not os.path.exists(path):
        return False
    image = cv2.imread(path)
    if image is None:
        return False
    height, width = image.shape[:2]
    if height == 0 or width == 0:
        return False
    aspect_ratio = max(width, height) / max(1, min(width, height))
    return aspect_ratio <= 10


def _has_enough_text(ad: Ad) -> bool:
    if ad.ocr_text is None:
        return False
    length = len(ad.ocr_text.strip())
    return 1 <= length <= 2000


def filter_noise(ads: Iterable[Ad]) -> Tuple[List[Ad], int]:
    """
    Remove ads that do not meet basic validity checks.

    Returns filtered ads and the number of dropped records.
    """

    filtered: List[Ad] = []
    dropped = 0

    for ad in ads:
        if not ad.ad_id:
            logger.debug("Dropping ad with missing ad_id")
            dropped += 1
            continue
        if not ad.creative_body and not (ad.ocr_text or "").strip():
            logger.debug("Dropping ad %s due to empty text fields", ad.ad_id)
            dropped += 1
            continue
        if not ad.image_path or not _is_image_valid(ad.image_path):
            logger.debug("Dropping ad %s due to invalid image", ad.ad_id)
            dropped += 1
            continue
        if not _has_enough_text(ad):
            logger.debug("Dropping ad %s due to insufficient OCR text", ad.ad_id)
            dropped += 1
            continue
        filtered.append(ad)

    logger.info("Filtered noise: kept %s ads, dropped %s", len(filtered), dropped)
    return filtered, dropped

