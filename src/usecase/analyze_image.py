from pathlib import Path
from typing import Dict

from src.core.tagging import describe_image
from src.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_images(image_paths: Dict[str, Path], ocr_results: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    descriptions: Dict[str, Dict[str, str]] = {}
    for ad_id, image_path in image_paths.items():
        text = ocr_results.get(ad_id, "")
        logger.info("Analyzing image for ad %s", ad_id)
        description = describe_image(image_path, text)
        descriptions[ad_id] = description
        logger.debug("Image description for %s: %s", ad_id, description)
    return descriptions
