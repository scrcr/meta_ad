from pathlib import Path
from typing import Dict

from src.interface.ocr_engine import OcrEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)


def ocr_text(engine: OcrEngine, image_paths: Dict[str, Path]) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for ad_id, image_path in image_paths.items():
        logger.info("Running OCR for ad %s", ad_id)
        text = engine.run(image_path)
        results[ad_id] = text
        logger.debug("OCR result for %s: %s", ad_id, text)
    return results
