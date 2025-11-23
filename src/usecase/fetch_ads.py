from typing import List

from src.core.ad import Ad
from src.interface.ads_repository import AdsRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_ads(repository: AdsRepository) -> List[Ad]:
    logger.info("Fetching ads from repository")
    ads = repository.fetch_recent_ads()
    logger.info("Fetched %d ads", len(ads))
    return ads
