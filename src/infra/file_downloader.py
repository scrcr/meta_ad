import json
from pathlib import Path
from typing import Dict

from src.core.ad import Ad
from src.interface.image_repository import ImageRepository


class FileDownloader(ImageRepository):
    _COLOR_MAP: Dict[str, tuple] = {
        "red": (220, 40, 40),
        "blue": (40, 90, 200),
        "green": (40, 170, 80),
        "gray": (180, 180, 180),
    }

    def _parse_color(self, snapshot_url: str) -> str:
        if snapshot_url.startswith("color:"):
            return snapshot_url.split(":", 1)[1]
        return "gray"

    def _write_ppm(self, path: Path, rgb: tuple[int, int, int], width: int = 160, height: int = 160) -> None:
        header = f"P6\n{width} {height}\n255\n".encode()
        pixel = bytes([rgb[0], rgb[1], rgb[2]])
        data = pixel * (width * height)
        with path.open("wb") as f:
            f.write(header + data)

    def download(self, ad: Ad, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        color = self._parse_color(ad.snapshot_url)
        rgb = self._COLOR_MAP.get(color, self._COLOR_MAP["gray"])
        image_path = output_dir / f"{ad.ad_id}_{color}.ppm"
        self._write_ppm(image_path, rgb)
        metadata = {
            "ad_id": ad.ad_id,
            "color": color,
            "width": 160,
            "height": 160,
            "creative_body": ad.creative_body,
            "advertiser": ad.advertiser,
        }
        meta_path = image_path.with_suffix(image_path.suffix + ".meta")
        meta_path.write_text(json.dumps(metadata))
        return image_path
