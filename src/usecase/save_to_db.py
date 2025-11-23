import asyncio
from typing import Iterable, List

from src.core.ad import Ad
from src.interface.storage_repository import StorageRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _serialize_ad(ad: Ad) -> dict:
    analysis = ad.analysis or None
    return {
        "id": ad.ad_id,
        "creative_body": ad.creative_body,
        "snapshot_url": ad.snapshot_url,
        "page_id": ad.page_id,
        "page_name": ad.page_name,
        "call_to_action_type": ad.call_to_action_type,
        "image_path": ad.image_path,
        "ocr_text": ad.ocr_text,
        "dominant_color": analysis.dominant_color if analysis else None,
        "has_person": analysis.has_person if analysis else None,
        "layout_type": analysis.layout_type if analysis else None,
        "pitch": analysis.pitch if analysis else None,
        "tags": ad.tags,
    }


async def save_ads(storage: StorageRepository, ads: Iterable[Ad]) -> None:
    records = [_serialize_ad(ad) for ad in ads]
    await storage.upsert(records)


def save_ads_sync(storage: StorageRepository, ads: Iterable[Ad]) -> None:
    asyncio.run(save_ads(storage, ads))
