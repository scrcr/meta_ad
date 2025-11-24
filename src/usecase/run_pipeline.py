import asyncio
from dataclasses import dataclass
from typing import List, Set

from src.config import PipelineConfig
from src.core.ad import Ad, RankedAd
from src.infra.file_downloader import FileDownloader
from src.infra.meta_ads_scraper import MetaAdsLibraryScraper
from src.infra.supabase_storage import SupabaseStorage
from src.infra.tesseract_engine import TesseractEngine
from src.usecase.analyze_image import analyze_ads
from src.usecase.dedupe import dedupe_ads
from src.usecase.download_images import download_ad_images
from src.usecase.fetch_ads import FetchResult, fetch_ads
from src.usecase.filter_noise import filter_noise
from src.usecase.generate_tags import attach_tags
from src.usecase.ocr_text import extract_text_from_ads
from src.usecase.render_html import HTMLRenderer
from src.usecase.save_to_db import save_ads
from src.usecase.trend import TrendAnalyzer, save_ranking
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class PipelineDependencies:
    ads_repo: MetaAdsLibraryScraper
    downloader: FileDownloader
    ocr_engine: TesseractEngine
    storage: SupabaseStorage
    renderer: HTMLRenderer


def build_components(config: PipelineConfig) -> PipelineDependencies:
    return PipelineDependencies(
        ads_repo=MetaAdsLibraryScraper(config.scraper),
        downloader=FileDownloader(config.data_dir),
        ocr_engine=TesseractEngine(),
        storage=SupabaseStorage(config.storage),
        renderer=HTMLRenderer(config.html_output),
    )


class PipelineRunner:
    def __init__(self, config: PipelineConfig, dependencies: PipelineDependencies) -> None:
        self.config = config
        self.deps = dependencies

    def run(self, limit: int) -> List[Ad]:
        return asyncio.run(self.run_async(limit))

    async def run_async(self, limit: int) -> List[Ad]:
        fetched = await asyncio.to_thread(self._fetch, limit)
        processed_ads = self._process_ads(fetched.ads)
        ranked_ads = self._rank(processed_ads)
        self._render(ranked_ads)
        await self._persist(processed_ads, fetched.new_page_ids)
        logger.info("Pipeline completed")
        return processed_ads

    def _fetch(self, limit: int) -> FetchResult:
        return fetch_ads(self.deps.ads_repo, limit)

    def _process_ads(self, ads: List[Ad]) -> List[Ad]:
        # 1. Download images (Immediate)
        ads = download_ad_images(self.deps.downloader, ads, self.config.data_dir)
        
        # 2. OCR
        ads = extract_text_from_ads(self.deps.ocr_engine, ads)
        
        # 3. Filter Noise
        ads, dropped_noise = filter_noise(ads)
        
        # 4. Dedupe
        ads, dropped_dupes = dedupe_ads(ads)
        
        logger.info(
            "Post-filter counts: %s valid ads (noise=%s, dupes=%s)",
            len(ads),
            dropped_noise,
            dropped_dupes,
        )
        
        # 5. Extract Features
        ads = analyze_ads(ads)
        
        # 6. Generate Tags
        ads = attach_tags(ads)
        return ads

    def _rank(self, ads: List[Ad]) -> List[RankedAd]:
        # 7. Trend/Score
        analyzer = TrendAnalyzer(ads)
        ranked = analyzer.rank_ads()
        save_ranking(ranked, self.config.ranking_output)
        return ranked

    def _render(self, ranked_ads: List[RankedAd]) -> None:
        # 8. Render HTML
        self.deps.renderer.render(ranked_ads)

    async def _persist(self, ads: List[Ad], new_page_ids: Set[str]) -> None:
        async with self.deps.storage as storage:
            await save_ads(storage, ads)
            if new_page_ids:
                await storage.upsert_page_ids(new_page_ids)


def run_pipeline(config: PipelineConfig, limit: int = 10) -> List[Ad]:
    dependencies = build_components(config)
    runner = PipelineRunner(config, dependencies)
    return runner.run(limit)


async def run_pipeline_async(config: PipelineConfig, limit: int = 10) -> List[Ad]:
    dependencies = build_components(config)
    runner = PipelineRunner(config, dependencies)
    return await runner.run_async(limit)
