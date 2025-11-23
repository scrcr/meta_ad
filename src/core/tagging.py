from collections import Counter
from typing import Iterable, List, Set

from src.core.ad import Ad, ImageAnalysis

COLOR_TAGS = {
    "red": ["urgent", "sale"],
    "blue": ["trust", "corporate"],
    "green": ["eco", "fresh"],
    "yellow": ["bright", "attention"],
    "purple": ["luxury"],
    "orange": ["energy", "fun"],
    "neutral": ["clean", "minimal"],
}


def _keyword_tags(text: str) -> Set[str]:
    keywords = {
        "free": "promotion",
        "sale": "discount",
        "limited": "scarcity",
        "new": "launch",
        "exclusive": "premium",
        "bundle": "pack",
    }
    lowered = text.lower()
    tags = {value for key, value in keywords.items() if key in lowered}
    return tags


def generate_concept_tags(ad: Ad, analysis: ImageAnalysis) -> List[str]:
    tags: Set[str] = set()
    tags.update(_keyword_tags(ad.creative_body))
    tags.update(_keyword_tags(ad.ocr_text or ""))

    for color_tag in COLOR_TAGS.get(analysis.dominant_color, []):
        tags.add(color_tag)

    if analysis.has_person:
        tags.add("human-centric")
    if analysis.layout_type == "text-heavy":
        tags.add("informational")
    if analysis.pitch == "rational":
        tags.add("rational")
    elif analysis.pitch == "emotional":
        tags.add("emotional")

    tags.add(analysis.dominant_color)
    return sorted(tags)


def summarize_tags(tags: Iterable[str]) -> List[str]:
    counter = Counter(tags)
    return [tag for tag, _ in counter.most_common()]
