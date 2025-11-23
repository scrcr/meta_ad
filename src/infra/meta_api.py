from typing import List

from src.core.ad import Ad
from src.interface.ads_repository import AdsRepository


class MetaAdsApiClient(AdsRepository):
    """Stub Meta Ads API client returning deterministic sample data."""

    def fetch_recent_ads(self) -> List[Ad]:
        return [
            Ad(
                ad_id="A001",
                advertiser="Acme Fitness",
                creative_body="Summer sale 50% off on all gear",
                snapshot_url="color:red",
                call_to_action="Shop Now",
            ),
            Ad(
                ad_id="A002",
                advertiser="Bright Travel",
                creative_body="New destinations for your dream vacation",
                snapshot_url="color:blue",
                call_to_action="Learn More",
            ),
            Ad(
                ad_id="A003",
                advertiser="Zen Foods",
                creative_body="Free trial meal plan for a healthy start",
                snapshot_url="color:green",
                call_to_action="Order",
            ),
        ]
