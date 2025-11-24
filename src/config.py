import os
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_GUARANTEE_PAGE_IDS: List[str] = [
    "153080620724",  # Nike
    "149018735138",  # Adidas
    "159215614156",  # Amazon
    "157701024255133",  # Walmart
    "132694903492716",  # Target
    "105930651496",  # eBay
    "150870234931907",  # Apple
    "119453128063",  # Samsung
    "128704263816190",  # Microsoft
    "354284978338083",  # Disney
    "7026104860",  # Netflix
    "6628568379",  # Starbucks
    "6274829895",  # McDonald's
    "343433529124603",  # Booking.com
    "145125257190900",  # Airbnb
    "161792550513040",  # Uber
    "274115262728775",  # Lyft
    "106389690742",  # Pepsi
    "344234965712",  # Coca-Cola
    "155021662189",  # Toyota
]

DEFAULT_HUMAN_USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
]

DEFAULT_EXPLORE_SEARCH_TERMS: List[str] = ["the", "a", "to", "for", "in"]


@dataclass
class ScraperConfig:
    page_ids: List[str] = field(default_factory=lambda: DEFAULT_GUARANTEE_PAGE_IDS)
    viewport_width: int = 1280
    viewport_height: int = 800
    locale: str = "en-GB"
    timezone: str = "Europe/London"
    headless: bool = True
    storage_state_path: str = os.path.join(".playwright", "meta_ads_context.json")
    user_agents: List[str] = field(default_factory=lambda: DEFAULT_HUMAN_USER_AGENTS)
    scroll_wait_min: float = 1.2
    scroll_wait_max: float = 2.4
    scroll_step: int = 300


@dataclass
class MetaApiConfig:
    access_token: str = ""
    account_id: str = ""
    page_size: int = 25
    guarantee_page_ids: List[str] = field(default_factory=lambda: DEFAULT_GUARANTEE_PAGE_IDS)
    ad_reached_countries: str = "GB"
    explore_search_terms: List[str] = field(default_factory=lambda: DEFAULT_EXPLORE_SEARCH_TERMS)


@dataclass
class StorageConfig:
    supabase_url: Optional[str]
    supabase_key: Optional[str]
    table: str = "ads"
    page_table: str = "pages"


@dataclass
class PipelineConfig:
    scraper: ScraperConfig
    storage: StorageConfig
    data_dir: str = os.path.join("data", "images")
    ranking_output: str = os.path.join("output", "ranking.json")

    @staticmethod
    def from_env() -> "PipelineConfig":
        def _parse_list(var: str, default: List[str]) -> List[str]:
            raw = os.getenv(var)
            if raw:
                parsed = [item.strip() for item in raw.split(",") if item.strip()]
                return parsed or default
            return default

        return PipelineConfig(
            scraper=ScraperConfig(
                page_ids=_parse_list("SCRAPE_PAGE_IDS", DEFAULT_GUARANTEE_PAGE_IDS),
                viewport_width=int(os.getenv("SCRAPER_VIEWPORT_WIDTH", "1280")),
                viewport_height=int(os.getenv("SCRAPER_VIEWPORT_HEIGHT", "800")),
                locale=os.getenv("SCRAPER_LOCALE", "en-GB"),
                timezone=os.getenv("SCRAPER_TIMEZONE", "Europe/London"),
                headless=os.getenv("SCRAPER_HEADLESS", "true").lower() != "false",
                storage_state_path=os.getenv(
                    "SCRAPER_STORAGE_STATE", os.path.join(".playwright", "meta_ads_context.json")
                ),
                user_agents=_parse_list("SCRAPER_USER_AGENTS", DEFAULT_HUMAN_USER_AGENTS),
                scroll_wait_min=float(os.getenv("SCRAPER_SCROLL_WAIT_MIN", "1.2")),
                scroll_wait_max=float(os.getenv("SCRAPER_SCROLL_WAIT_MAX", "2.4")),
                scroll_step=int(os.getenv("SCRAPER_SCROLL_STEP", "300")),
            ),
            storage=StorageConfig(
                supabase_url=os.getenv("SUPABASE_URL"),
                supabase_key=os.getenv("SUPABASE_KEY"),
                table=os.getenv("SUPABASE_TABLE", "ads"),
                page_table=os.getenv("SUPABASE_PAGE_TABLE", "pages"),
            ),
            data_dir=os.getenv("DATA_DIR", os.path.join("data", "images")),
            ranking_output=os.getenv("RANKING_OUTPUT", os.path.join("output", "ranking.json")),
        )
