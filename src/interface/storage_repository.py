from abc import ABC, abstractmethod
from typing import Dict, List

from src.core.ad import Ad


class StorageRepository(ABC):
    @abstractmethod
    def store_ad(self, ad: Ad) -> None:
        raise NotImplementedError

    @abstractmethod
    def store_image(self, ad_id: str, image_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def store_ocr(self, ad_id: str, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def store_tags(self, ad_id: str, tags: List[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def fetch_tag_ranking(self) -> List[Dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError
