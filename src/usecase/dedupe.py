from __future__ import annotations

import hashlib
from typing import Iterable, List, Tuple

import cv2
import numpy as np

from src.core.ad import Ad
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _normalize_text(ad: Ad) -> str:
    return (ad.creative_body + " " + (ad.ocr_text or "")).strip().lower()


def _text_hash(ad: Ad) -> str:
    normalized = _normalize_text(ad)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _phash(image_path: str) -> int:
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Unable to load image at {image_path}")
    resized = cv2.resize(image, (32, 32))
    dct = cv2.dct(np.float32(resized))
    dct_low = dct[:8, :8]
    median = np.median(dct_low)
    bits = dct_low > median
    hash_value = 0
    for bit in bits.flatten():
        hash_value = (hash_value << 1) | int(bit)
    return hash_value


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def dedupe_ads(ads: Iterable[Ad], phash_threshold: int = 5) -> Tuple[List[Ad], int]:
    """Deduplicate ads using text hash first, then perceptual hash."""

    text_seen: set[str] = set()
    image_hashes: List[int] = []
    unique: List[Ad] = []
    dropped = 0

    for ad in ads:
        ad.text_hash = _text_hash(ad)
        if ad.text_hash in text_seen:
            logger.debug("Dropping ad %s due to text hash duplicate", ad.ad_id)
            dropped += 1
            continue

        if ad.image_path:
            try:
                ad.phash = _phash(ad.image_path)
            except Exception as exc:  # noqa: BLE001
                logger.debug("Failed to compute pHash for ad %s: %s", ad.ad_id, exc)
                ad.phash = None

        is_duplicate = False
        if ad.phash is not None:
            for existing in image_hashes:
                if _hamming(existing, ad.phash) <= phash_threshold:
                    is_duplicate = True
                    break

        if is_duplicate:
            logger.debug("Dropping ad %s due to perceptual hash match", ad.ad_id)
            dropped += 1
            continue

        text_seen.add(ad.text_hash)
        if ad.phash is not None:
            image_hashes.append(ad.phash)
        unique.append(ad)

    logger.info("Deduplicated ads: kept %s, dropped %s", len(unique), dropped)
    return unique, dropped

