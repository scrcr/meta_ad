from abc import ABC, abstractmethod
from pathlib import Path

from src.core.ad import Ad


class ImageRepository(ABC):
    @abstractmethod
    def download(self, ad: Ad, output_dir: Path) -> Path:
        raise NotImplementedError
