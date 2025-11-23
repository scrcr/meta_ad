from typing import Iterable, List

from src.core.ad import Ad
from src.interface.ocr_engine import OCREngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_ads(engine: OCREngine, ads: Iterable[Ad]) -> List[Ad]:
    processed: List[Ad] = []
    for ad in ads:
        if not ad.image_path:
            logger.warning("Skipping OCR for ad %s due to missing image", ad.ad_id)
            processed.append(ad)
            continue
        try:
            ad.ocr_text = engine.extract_text(ad.image_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("OCR failed for ad %s: %s", ad.ad_id, exc)
            ad.ocr_text = ""
        processed.append(ad)
    return processed
