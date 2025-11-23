from typing import Dict, List

from src.core.tagging import tags_from_description
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_tags(image_descriptions: Dict[str, Dict[str, str]], ocr_results: Dict[str, str]) -> Dict[str, List[str]]:
    tags: Dict[str, List[str]] = {}
    for ad_id, description in image_descriptions.items():
        combined = list(tags_from_description(description))
        text = ocr_results.get(ad_id, "")
        if text:
            combined.append(f"text:{text[:20].strip()}")
        logger.info("Generated %d tags for ad %s", len(combined), ad_id)
        tags[ad_id] = combined
    return tags
