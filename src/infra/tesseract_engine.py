import json
from pathlib import Path

from src.interface.ocr_engine import OcrEngine


class SimpleTesseractEngine(OcrEngine):
    """Lightweight OCR stub that pulls text from generated metadata."""

    def run(self, image_path: Path) -> str:
        meta_path = image_path.with_suffix(image_path.suffix + ".meta")
        if meta_path.exists():
            data = json.loads(meta_path.read_text())
            return data.get("creative_body", "")
        return ""
