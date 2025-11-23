import requests
from typing import Dict, Iterable, List, Optional, Set

from src.config import MetaApiConfig
from src.core.ad import Ad
from src.interface.ads_repository import AdsRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetaApi(AdsRepository):
    base_url = "https://graph.facebook.com/v18.0"

    def __init__(self, config: MetaApiConfig) -> None:
        self.config = config
        if not config.access_token:
            logger.warning("Meta access token missing; API calls will fail.")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.config.access_token}"}

    def _extract_ads(self, items: Iterable[Dict[str, object]], remaining: int) -> List[Ad]:
        ads: List[Ad] = []
        for item in items:
            creative = item.get("creative", {}) or {}
            snapshot_url = creative.get("image_url") or creative.get("thumbnail_url") or ""
            ads.append(
                Ad(
                    ad_id=str(item.get("id", "")),
                    creative_body=(creative.get("body") or ""),
                    snapshot_url=snapshot_url,
                    page_id=item.get("page_id"),
                    page_name=item.get("page_name"),
                    call_to_action_type=item.get("call_to_action_type"),
                )
            )
            remaining -= 1
            if remaining == 0:
                break
        return ads

    def _fetch_ads(self, params: Dict[str, object], limit: int) -> List[Ad]:
        ads: List[Ad] = []
        remaining = limit
        next_url: Optional[str] = f"{self.base_url}/ads_archive"
        next_params: Optional[Dict[str, object]] = {**params, "limit": min(limit, self.config.page_size)}

        while next_url and remaining > 0:
            response = requests.get(next_url, headers=self._headers(), params=next_params, timeout=20)
            response.raise_for_status()
            data = response.json()
            items = data.get("data", []) if isinstance(data, dict) else []
            ads.extend(self._extract_ads(items, remaining))
            remaining = max(0, limit - len(ads))
            paging = data.get("paging", {}) if isinstance(data, dict) else {}
            next_url = paging.get("next") if isinstance(paging, dict) else None
            next_params = None  # next already includes cursor & params
            if next_url:
                logger.debug("Following paging link for next batch")
        logger.info("Fetched %s ads with params=%s", len(ads), params)
        return ads

    def fetch_guarantee_ads(self, limit: int) -> List[Ad]:
        params: Dict[str, object] = {
            "fields": "id,page_id,page_name,creative{body,image_url},call_to_action_type",
            "ad_delivery_mode": "GUARANTEE",
            "search_page_ids": ",".join(self.config.guarantee_page_ids),
            "ad_reached_countries": self.config.ad_reached_countries,
        }
        return self._fetch_ads(params=params, limit=limit)

    def fetch_explore_ads(self, limit: int) -> List[Ad]:
        ads: List[Ad] = []
        discovered_pages: Set[str] = set()
        per_term = max(1, limit // max(1, len(self.config.explore_search_terms)))

        for term in self.config.explore_search_terms:
            if len(ads) >= limit:
                break
            params = {
                "fields": "id,page_id,page_name,creative{body,image_url},call_to_action_type",
                "ad_delivery_mode": "EXPLORE",
                "search_terms": term,
                "ad_reached_countries": self.config.ad_reached_countries,
            }
            batch = self._fetch_ads(params=params, limit=per_term)
            ads.extend(batch)
            for ad in batch:
                if ad.page_id:
                    discovered_pages.add(ad.page_id)

        self.new_page_ids: Set[str] = discovered_pages
        logger.info("Explore discovered %s unique page_ids", len(self.new_page_ids))
        return ads[:limit]
