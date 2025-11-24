import os
from typing import List

from src.core.ad import RankedAd
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HTMLRenderer:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def render(self, ranked_ads: List[RankedAd]) -> None:
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        html_content = self._generate_html(ranked_ads)
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info("Generated HTML report at %s", self.output_path)

    def _generate_html(self, ranked_ads: List[RankedAd]) -> str:
        rows = []
        for item in ranked_ads:
            image_url = f"../data/images/{os.path.basename(item.ad.image_path)}" if item.ad.image_path else ""
            tags_str = ", ".join(item.ad.tags)
            rows.append(f"""
                <div class="ad-card">
                    <div class="rank">#{item.rank}</div>
                    <div class="score">Score: {item.score:.2f}</div>
                    <img src="{image_url}" alt="Ad Image" loading="lazy">
                    <div class="details">
                        <p><strong>ID:</strong> {item.ad.ad_id}</p>
                        <p><strong>Tags:</strong> {tags_str}</p>
                        <p><strong>Color:</strong> {item.ad.analysis.dominant_color if item.ad.analysis else 'N/A'}</p>
                    </div>
                </div>
            """)
            
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meta Ads Ranking</title>
    <style>
        body {{ font-family: sans-serif; max_width: 1200px; margin: 0 auto; padding: 20px; background: #f0f2f5; }}
        h1 {{ text-align: center; color: #1c1e21; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .ad-card {{ background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .rank {{ font-size: 1.5em; font-weight: bold; color: #1877f2; }}
        .score {{ color: #65676b; margin-bottom: 10px; }}
        img {{ width: 100%; height: auto; border-radius: 4px; }}
        .details {{ margin-top: 10px; font-size: 0.9em; }}
        .details p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>Daily Meta Ads Ranking</h1>
    <div class="grid">
        {"".join(rows)}
    </div>
</body>
</html>
"""
