from typing import Iterable, List, Set, Tuple

from src.core.ad import Ad
from src.interface.ads_repository import AdsRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_ads(repository: AdsRepository, limit: int) -> Tuple[List[Ad], Set[str]]:
    guarantee = repository.fetch_guarantee_ads(limit)
    explore = repository.fetch_explore_ads(limit)
    combined: List[Ad] = [*guarantee, *explore]
    new_page_ids: Set[str] = set()
    if hasattr(repository, "new_page_ids"):
        new_page_ids = set(getattr(repository, "new_page_ids"))
    logger.info(
        "Fetched %s ads (guarantee=%s, explore=%s) with %s new page_ids",
        len(combined),
        len(guarantee),
        len(explore),
        len(new_page_ids),
    )
    return combined, new_page_ids
