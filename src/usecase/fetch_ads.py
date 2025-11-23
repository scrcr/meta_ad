from dataclasses import dataclass
from typing import List, Set

from src.core.ad import Ad
from src.interface.ads_repository import AdsRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FetchResult:
    ads: List[Ad]
    new_page_ids: Set[str]


def _collect_new_page_ids(repository: AdsRepository) -> Set[str]:
    """Safely pull discovered page IDs from the repository if available."""

    candidate_ids = getattr(repository, "new_page_ids", set())
    if isinstance(candidate_ids, set):
        return candidate_ids
    return set(candidate_ids)


def fetch_ads(repository: AdsRepository, limit: int) -> FetchResult:
    guarantee = repository.fetch_guarantee_ads(limit)
    explore = repository.fetch_explore_ads(limit)
    combined: List[Ad] = [*guarantee, *explore]
    new_page_ids = _collect_new_page_ids(repository)
    logger.info(
        "Fetched %s ads (guarantee=%s, explore=%s) with %s new page_ids",
        len(combined),
        len(guarantee),
        len(explore),
        len(new_page_ids),
    )
    return FetchResult(ads=combined, new_page_ids=new_page_ids)
