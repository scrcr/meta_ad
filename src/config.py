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

DEFAULT_EXPLORE_SEARCH_TERMS: List[str] = ["the", "a", "to", "for", "in"]


@dataclass
class MetaApiConfig:
    access_token: str
    account_id: str
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
    meta_api: MetaApiConfig
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
            meta_api=MetaApiConfig(
                access_token=os.getenv("META_ACCESS_TOKEN", ""),
                account_id=os.getenv("META_ACCOUNT_ID", ""),
                page_size=int(os.getenv("META_PAGE_SIZE", "25")),
                guarantee_page_ids=_parse_list("GUARANTEE_PAGE_IDS", DEFAULT_GUARANTEE_PAGE_IDS),
                ad_reached_countries=os.getenv("AD_REACHED_COUNTRIES", "GB"),
                explore_search_terms=_parse_list("EXPLORE_SEARCH_TERMS", DEFAULT_EXPLORE_SEARCH_TERMS),
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
