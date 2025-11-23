from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Ad:
    """Simple data holder for advertisement metadata."""

    ad_id: str
    advertiser: str
    creative_body: str
    snapshot_url: str
    call_to_action: Optional[str] = None
