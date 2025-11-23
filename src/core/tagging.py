from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore

try:  # OpenCV is optional.
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore

try:  # Pillow is optional.
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Image = None  # type: ignore


_RGB_FALLBACK = {
    "red": (220, 40, 40),
    "green": (40, 170, 80),
    "blue": (40, 90, 200),
    "gray": (180, 180, 180),
}


def _load_metadata(image_path: Path) -> Dict[str, object]:
    meta_path = image_path.with_suffix(image_path.suffix + ".meta")
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    return {}


def _color_name_from_rgb(mean_rgb: Tuple[float, float, float]) -> str:
    r, g, b = mean_rgb
    primary = max([(r, "red"), (g, "green"), (b, "blue")], key=lambda x: x[0])[1]
    brightness = (r + g + b) / (3 * 255)
    if brightness > 0.8:
        return f"bright-{primary}"
    if brightness < 0.2:
        return f"dark-{primary}"
    return primary


def _load_with_pillow(image_path: Path):
    if Image is None:
        raise RuntimeError("Pillow is not available")
    with Image.open(image_path) as img:
        return img.convert("RGB")


def _load_with_opencv(image_path: Path):
    if cv2 is None:
        raise RuntimeError("OpenCV is not available")
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"Failed to read image: {image_path}")
    return image[:, :, ::-1]  # Convert BGR to RGB


def _load_image_rgb(image_path: Path):
    metadata = _load_metadata(image_path)
    if metadata:
        color = metadata.get("color", "gray")
        rgb = _RGB_FALLBACK.get(str(color), _RGB_FALLBACK["gray"])
        return rgb, metadata.get("width", 1), metadata.get("height", 1)

    if cv2 is not None:
        image = _load_with_opencv(image_path)
        return image, image.shape[1], image.shape[0]
    if Image is not None:
        img = _load_with_pillow(image_path)
        return img, img.width, img.height
    raise RuntimeError("No image backend available")


def _compute_mean_rgb(image) -> Tuple[float, float, float]:
    if np is not None and hasattr(image, "shape"):
        mean_channels = tuple(np.mean(image.reshape(-1, 3), axis=0))  # type: ignore[arg-type]
        r, g, b = mean_channels[0], mean_channels[1], mean_channels[2]
        return r, g, b
    if Image is not None and hasattr(image, "getdata"):
        pixels = list(image.getdata())
        total = [0.0, 0.0, 0.0]
        for r, g, b in pixels:
            total[0] += r
            total[1] += g
            total[2] += b
        count = len(pixels)
        return total[0] / count, total[1] / count, total[2] / count
    # Fallback when only metadata is available
    if isinstance(image, tuple) and len(image) == 3:
        return image[0], image[1], image[2]
    return 128.0, 128.0, 128.0


def dominant_color_tag(image_source) -> str:
    mean_rgb = _compute_mean_rgb(image_source)
    return _color_name_from_rgb(mean_rgb)


def detect_layout_tag(width: int, height: int) -> str:
    ratio = width / height if height else 1.0
    if ratio > 1.2:
        return "landscape"
    if ratio < 0.8:
        return "portrait"
    return "square"


def detect_person_presence(mean_rgb: Tuple[float, float, float]) -> str:
    brightness = sum(mean_rgb) / (3 * 255)
    if brightness > 0.85:
        return "maybe-person"
    return "no-person"


def detect_pitch_tag(text: str) -> str:
    lowered = text.lower()
    if "sale" in lowered or "%" in lowered:
        return "discount"
    if any(word in lowered for word in ["new", "launch", "introducing"]):
        return "announcement"
    if any(word in lowered for word in ["free", "trial", "demo"]):
        return "trial"
    return "generic"


def describe_image(image_path: Path, ocr_text: str) -> Dict[str, str]:
    metadata = _load_metadata(image_path)
    image_rgb, width, height = _load_image_rgb(image_path)
    mean_rgb = _compute_mean_rgb(image_rgb)

    return {
        "color": dominant_color_tag(image_rgb),
        "layout": detect_layout_tag(int(width), int(height)),
        "person": detect_person_presence(mean_rgb),
        "pitch": detect_pitch_tag(ocr_text or metadata.get("creative_body", "")),
    }


def tags_from_description(description: Dict[str, str]) -> List[str]:
    return list(description.values())
