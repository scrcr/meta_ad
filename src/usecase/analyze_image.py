import cv2
import numpy as np
from typing import Iterable, List

from src.core.ad import Ad, ImageAnalysis
from src.utils.logger import get_logger

logger = get_logger(__name__)


COLOR_BOUNDS = {
    "red": ((0, 50, 50), (10, 255, 255)),
    "orange": ((11, 50, 50), (25, 255, 255)),
    "yellow": ((26, 50, 50), (35, 255, 255)),
    "green": ((36, 50, 50), (85, 255, 255)),
    "blue": ((86, 50, 50), (125, 255, 255)),
    "purple": ((126, 50, 50), (160, 255, 255)),
}


def dominant_color_label(image: np.ndarray) -> str:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    scores = {}
    for label, (lower, upper) in COLOR_BOUNDS.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        scores[label] = int(mask.sum())
    if not scores:
        return "neutral"
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "neutral"
    return best


def detect_person(image: np.ndarray) -> bool:
    cascade_path = cv2.data.haarcascades + "haarcascade_fullbody.xml"
    classifier = cv2.CascadeClassifier(cascade_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detections = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
    return len(detections) > 0


def layout_type(image: np.ndarray) -> str:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    density = edges.mean() / 255
    if density > 0.25:
        return "text-heavy"
    if density > 0.15:
        return "balanced"
    return "visual"


def pitch_type(ad: Ad, layout: str, has_person: bool) -> str:
    text = (ad.creative_body + " " + (ad.ocr_text or "")).lower()
    rational_keywords = ["save", "price", "discount", "offer", "plan", "guarantee"]
    emotional_keywords = ["love", "feel", "happy", "inspire", "dream", "story"]

    rational_hits = sum(1 for k in rational_keywords if k in text)
    emotional_hits = sum(1 for k in emotional_keywords if k in text)

    if rational_hits > emotional_hits:
        return "rational"
    if emotional_hits > rational_hits:
        return "emotional"
    if layout == "visual" and has_person:
        return "emotional"
    return "balanced"


def analyze_ads(ads: Iterable[Ad]) -> List[Ad]:
    analyzed: List[Ad] = []
    for ad in ads:
        if not ad.image_path:
            logger.warning("Skipping analysis for ad %s due to missing image", ad.ad_id)
            analyzed.append(ad)
            continue
        image = cv2.imread(ad.image_path)
        if image is None:
            logger.error("Failed to load image for ad %s from %s", ad.ad_id, ad.image_path)
            analyzed.append(ad)
            continue
        color = dominant_color_label(image)
        person_present = detect_person(image)
        layout = layout_type(image)
        pitch = pitch_type(ad, layout, person_present)
        ad.analysis = ImageAnalysis(
            dominant_color=color,
            has_person=person_present,
            layout_type=layout,
            pitch=pitch,
            extra={"image_shape": image.shape},
        )
        analyzed.append(ad)
    return analyzed
