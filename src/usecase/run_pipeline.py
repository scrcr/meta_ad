import asyncio
from typing import List

from src.config import PipelineConfig
from src.core.ad import Ad
from src.infra.file_downloader import FileDownloader
from src.infra.meta_api import MetaApi
from src.infra.supabase_storage import SupabaseStorage
from src.infra.tesseract_engine import TesseractEngine
from src.usecase.analyze_image import analyze_ads
from src.usecase.dedupe import dedupe_ads
from src.usecase.download_images import download_ad_images
from src.usecase.fetch_ads import fetch_ads
from src.usecase.filter_noise import filter_noise
from src.usecase.generate_tags import attach_tags
from src.usecase.ocr_text import extract_text_from_ads
from src.usecase.ranking import rank_ads, save_ranking
from src.usecase.save_to_db import save_ads
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_components(config: PipelineConfig):
    ads_repo = MetaApi(config.meta_api)
    downloader = FileDownloader(config.data_dir)
    ocr_engine = TesseractEngine()
    storage = SupabaseStorage(config.storage)
    return ads_repo, downloader, ocr_engine, storage


async def run_pipeline_async(config: PipelineConfig, limit: int = 10) -> List[Ad]:
    ads_repo, downloader, ocr_engine, storage = build_components(config)
    ads, new_page_ids = fetch_ads(ads_repo, limit)
    ads = download_ad_images(downloader, ads, config.data_dir)
    ads = extract_text_from_ads(ocr_engine, ads)
    ads, dropped_noise = filter_noise(ads)
    ads, dropped_dupes = dedupe_ads(ads)
    logger.info("Post-filter counts: %s valid ads (noise=%s, dupes=%s)", len(ads), dropped_noise, dropped_dupes)
    ads = analyze_ads(ads)
    ads = attach_tags(ads)
    ranked = rank_ads(ads)
    save_ranking(ranked, config.ranking_output)
    await save_ads(storage, ads)
    if new_page_ids:
        await storage.upsert_page_ids(new_page_ids)
    await storage.close()
    logger.info("Pipeline completed")
    return ads


def run_pipeline(config: PipelineConfig, limit: int = 10) -> List[Ad]:
    return asyncio.run(run_pipeline_async(config, limit))
