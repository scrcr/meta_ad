import json
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.core.ad import Ad, RankedAd
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrendMetrics:
    freq_today: int = 0
    freq_yesterday: int = 0
    ma3_today: float = 0.0
    ma3_yesterday: float = 0.0
    impr_today: int = 0
    impr_yesterday: int = 0


@dataclass
class TrendScore:
    count_score: float = 0.0
    impr_score: Optional[float] = None
    selected_type: str = "count"  # 'count' or 'impr'


class TrendAnalyzer:
    def __init__(self, ads: List[Ad], history: Dict[str, TrendMetrics] = None):
        self.ads = ads
        self.history = history or {}
        self.tag_counts = Counter()
        for ad in ads:
            for tag in ad.tags:
                self.tag_counts[tag] += 1

    def calculate_scores(self) -> Dict[str, TrendScore]:
        scores = {}
        for tag, freq in self.tag_counts.items():
            metrics = self.history.get(tag, TrendMetrics())
            
            # Count Score
            rate = (freq - metrics.freq_yesterday) / (metrics.freq_yesterday + 1)
            persistence = metrics.ma3_today / (metrics.ma3_yesterday + 1)
            count_score = rate + persistence

            # Impr Score (Placeholder as we don't have real impr data yet)
            impr_score = None
            
            scores[tag] = TrendScore(count_score=count_score, impr_score=impr_score)
        return scores

    def rank_ads(self) -> List[RankedAd]:
        # Simple ranking based on count score of the ad's most significant tag
        # In a real scenario, we might aggregate scores of all tags
        
        scores = self.calculate_scores()
        
        scored_ads = []
        for ad in self.ads:
            max_score = 0.0
            for tag in ad.tags:
                if tag in scores:
                    max_score = max(max_score, scores[tag].count_score)
            scored_ads.append((ad, max_score))
            
        scored_ads.sort(key=lambda x: x[1], reverse=True)
        
        return [
            RankedAd(ad=ad, score=score, rank=i + 1)
            for i, (ad, score) in enumerate(scored_ads)
        ]


def save_ranking(ranked_ads: List[RankedAd], path: str) -> None:
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
