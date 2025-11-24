import os
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_GUARANTEE_PAGE_IDS_PATH = os.path.join("data", "guarantee_page_ids.txt")
DEFAULT_EXPLORE_TERMS_PATH = os.path.join("data", "explore_terms.txt")

DEFAULT_HUMAN_USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
]


@dataclass
class ScraperConfig:
    page_ids: List[str] = field(default_factory=list)
    explore_search_terms: List[str] = field(default_factory=list)
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
    guarantee_page_ids: List[str] = field(default_factory=list)
    ad_reached_countries: str = "GB"
    explore_search_terms: List[str] = field(default_factory=list)


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
    html_output: str = os.path.join("output", "index.html")

    @staticmethod
    def from_env() -> "PipelineConfig":
        def _read_lines(path: str) -> List[str]:
            if not os.path.exists(path):
                return []
            with open(path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]

        def _parse_list(var: str, default: List[str]) -> List[str]:
            raw = os.getenv(var)
            if raw:
                parsed = [item.strip() for item in raw.split(",") if item.strip()]
                return parsed or default
            return default

        page_ids = _read_lines(DEFAULT_GUARANTEE_PAGE_IDS_PATH)
        explore_terms = _read_lines(DEFAULT_EXPLORE_TERMS_PATH)

        # Allow env var override
        page_ids = _parse_list("SCRAPE_PAGE_IDS", page_ids)

        return PipelineConfig(
            scraper=ScraperConfig(
                page_ids=page_ids,
                explore_search_terms=explore_terms,
                viewport_width=int(os.getenv("SCRAPER_VIEWPORT_WIDTH", "1280")),
                viewport_height=int(os.getenv("SCRAPER_VIEWPORT_HEIGHT", "800")),
                locale=os.getenv("SCRAPER_LOCALE", "en-GB"),
                timezone=os.getenv("SCRAPER_TIMEZONE", "Europe/London"),
                headless=os.getenv("SCRAPER_HEADLESS", "false").lower() != "false",
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
            html_output=os.getenv("HTML_OUTPUT", os.path.join("output", "index.html")),
        )
