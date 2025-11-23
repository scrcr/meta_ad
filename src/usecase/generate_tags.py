from typing import Iterable, List

from src.core.ad import Ad
from src.core.tagging import generate_concept_tags
from src.utils.logger import get_logger

logger = get_logger(__name__)


def attach_tags(ads: Iterable[Ad]) -> List[Ad]:
    enriched: List[Ad] = []
    for ad in ads:
        if ad.analysis is None:
            logger.warning("Skipping tag generation for ad %s without analysis", ad.ad_id)
            enriched.append(ad)
            continue
        ad.tags = generate_concept_tags(ad, ad.analysis)
        enriched.append(ad)
    return enriched
