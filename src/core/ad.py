from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Ad:
    ad_id: str
    creative_body: str
    snapshot_url: str
    page_id: Optional[str] = None
    page_name: Optional[str] = None
    call_to_action_type: Optional[str] = None
    image_path: Optional[str] = None
    ocr_text: Optional[str] = None
    analysis: Optional["ImageAnalysis"] = None
    text_hash: Optional[str] = None
    phash: Optional[int] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ImageAnalysis:
    dominant_color: str
    has_person: bool
    layout_type: str
    pitch: str
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankedAd:
    ad: Ad
    score: float
    rank: int
