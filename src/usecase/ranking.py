import json
import os
from typing import Iterable, List

from src.core.ad import Ad, RankedAd
from src.core.tagging import summarize_tags
from src.utils.logger import get_logger

logger = get_logger(__name__)


def score_ad(ad: Ad) -> float:
    score = 0.0
    if ad.analysis:
        if ad.analysis.has_person:
            score += 1.5
        if ad.analysis.layout_type == "balanced":
            score += 1.0
        elif ad.analysis.layout_type == "visual":
            score += 0.5
        if ad.analysis.pitch == "emotional":
            score += 1.2
        elif ad.analysis.pitch == "rational":
            score += 1.0
    score += len(ad.tags) * 0.2
    if ad.call_to_action_type:
        score += 0.3
    return round(score, 3)


def rank_ads(ads: Iterable[Ad]) -> List[RankedAd]:
    scored = [(ad, score_ad(ad)) for ad in ads]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [RankedAd(ad=ad, score=score, rank=index + 1) for index, (ad, score) in enumerate(scored)]


def save_ranking(ranked_ads: Iterable[RankedAd], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    serialized = [
        {
            "rank": item.rank,
            "score": item.score,
            "ad_id": item.ad.ad_id,
            "tags": item.ad.tags,
            "dominant_color": item.ad.analysis.dominant_color if item.ad.analysis else None,
        }
        for item in ranked_ads
    ]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(serialized, file, indent=2)
    logger.info("Saved ranking to %s", path)


def summarize_tagspace(ranked_ads: Iterable[RankedAd]) -> List[str]:
    all_tags = []
    for item in ranked_ads:
        all_tags.extend(item.ad.tags)
    return summarize_tags(all_tags)
