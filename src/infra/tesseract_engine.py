import cv2
import numpy as np
import pytesseract

from src.interface.ocr_engine import OCREngine


class TesseractEngine(OCREngine):
    def __init__(self) -> None:
        self.config = "--oem 3 --psm 6"

    def _preprocess(self, image_path: str) -> 'np.ndarray':
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_text(self, image_path: str) -> str:
        processed = self._preprocess(image_path)
        text = pytesseract.image_to_string(processed, config=self.config)
        return text.strip()
