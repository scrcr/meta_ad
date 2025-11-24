import random
from pathlib import Path
from typing import List

from playwright.sync_api import Page, sync_playwright

from src.config import ScraperConfig
from src.core.ad import Ad
from src.interface.ads_repository import AdsRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetaAdsLibraryScraper(AdsRepository):
    """Scrape the Meta Ads Library web UI with human-like pacing."""

    base_url = (
        "https://www.facebook.com/ads/library/?active_status=all&view_all_page_id={page_id}"
    )

    def __init__(self, config: ScraperConfig) -> None:
        self.config = config
        self.new_page_ids = set()
        self._storage_state_path = Path(config.storage_state_path)
        self._storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    # -- Public API -----------------------------------------------------
    def fetch_guarantee_ads(self, limit: int) -> List[Ad]:
        ads: List[Ad] = []
        with sync_playwright() as playwright:
            browser = self._launch_browser(playwright)
            context = self._build_context(browser)
            page = context.new_page()

            for page_id in self.config.page_ids:
                if len(ads) >= limit:
                    break
                ads.extend(self._scrape_page(page, page_id, remaining=limit - len(ads)))
                self._human_pause(page)

            context.storage_state(path=str(self._storage_state_path))
            context.close()
            browser.close()

        logger.info("Scraped %s ads across %s pages", len(ads), len(self.config.page_ids))
        return ads[:limit]

    def fetch_explore_ads(self, limit: int) -> List[Ad]:
        # Web scraping mode does not perform explore discovery; keep the contract.
        self.new_page_ids = set()
        return []

    # -- Helpers --------------------------------------------------------
    def _launch_browser(self, playwright):
        return playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

    def _build_context(self, browser):
        user_agent = random.choice(self.config.user_agents)
        storage_state = str(self._storage_state_path) if self._storage_state_path.exists() else None
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
            locale=self.config.locale,
            timezone_id=self.config.timezone,
            storage_state=storage_state,
        )
        logger.info("Using UA=%s, locale=%s, timezone=%s", user_agent, self.config.locale, self.config.timezone)
        return context

    def _scrape_page(self, page: Page, page_id: str, remaining: int) -> List[Ad]:
        url = self.base_url.format(page_id=page_id)
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(random.uniform(1200, 2000))
        self._slow_scroll(page)
        cards = self._extract_cards(page)

        ads: List[Ad] = []
        for idx, card in enumerate(cards):
            if len(ads) >= remaining:
                break
            ad = self._extract_ad_from_card(card, page_id=page_id, fallback_idx=idx)
            if ad:
                ads.append(ad)
        logger.info("Page %s yielded %s ads (requested %s)", page_id, len(ads), remaining)
        return ads

    def _slow_scroll(self, page: Page) -> None:
        last_height = 0
        while True:
            page.evaluate(f"window.scrollBy(0, {self.config.scroll_step})")
            page.wait_for_timeout(random.uniform(self.config.scroll_wait_min * 1000, self.config.scroll_wait_max * 1000))
            height = page.evaluate("document.body.scrollHeight")
            if height == last_height:
                break
            last_height = height

    def _extract_cards(self, page: Page):
        selectors = [
            "div[data-ad-preview-id]",
            "div[data-pagelet^='ad_lib_researcher_ad']",
            "div[role='article']",
        ]
        for selector in selectors:
            cards = page.query_selector_all(selector)
            if cards:
                return cards
        return []

    def _extract_ad_from_card(self, card, page_id: str, fallback_idx: int) -> Ad | None:
        ad_id = (
            card.get_attribute("data-ad-preview-id")
            or card.get_attribute("data-adid")
            or card.get_attribute("data-ad-id")
        )
        if not ad_id:
            ad_id = f"{page_id}-{fallback_idx+1}"

        snapshot_url = self._extract_image(card)
        creative_body = self._extract_text(card)
        if not snapshot_url and not creative_body:
            return None

        return Ad(
            ad_id=str(ad_id),
            creative_body=creative_body,
            snapshot_url=snapshot_url or "",
            page_id=page_id,
        )

    def _extract_image(self, card) -> str | None:
        image = card.query_selector("img")
        if image:
            return image.get_attribute("src") or image.get_attribute("data-src")
        return None

    def _extract_text(self, card) -> str:
        candidates = [
            card.query_selector("[data-ad-text]") or card.query_selector("[role='presentation']"),
            card.query_selector("div[dir='auto']"),
        ]
        for node in candidates:
            if node:
                text = node.inner_text().strip()
                if text:
                    return text
        return (card.inner_text() or "").strip()

    def _human_pause(self, page: Page) -> None:
        pause_ms = random.uniform(10_000, 60_000)
        logger.debug("Sleeping for %.2f seconds before next page", pause_ms / 1000)
        page.wait_for_timeout(pause_ms)
