from abc import ABC, abstractmethod
from typing import Iterable


class ImageRepository(ABC):
    @abstractmethod
    def download(self, url: str, dest_path: str) -> str:
        raise NotImplementedError

    def bulk_download(self, items: Iterable[tuple[str, str]]) -> list[str]:
        paths = []
        for url, dest_path in items:
            paths.append(self.download(url, dest_path))
        return paths
