from abc import ABC, abstractmethod
from pathlib import Path


class OcrEngine(ABC):
    @abstractmethod
    def run(self, image_path: Path) -> str:
        raise NotImplementedError
