from abc import ABC, abstractmethod
from typing import Iterable, List

from src.core.ad import Ad


class AdsRepository(ABC):
    @abstractmethod
    def fetch_guarantee_ads(self, limit: int) -> List[Ad]:
        raise NotImplementedError

    @abstractmethod
    def fetch_explore_ads(self, limit: int) -> List[Ad]:
        raise NotImplementedError

    def fetch_all(self, limit: int) -> Iterable[Ad]:
        for ad in self.fetch_guarantee_ads(limit):
            yield ad
        for ad in self.fetch_explore_ads(limit):
            yield ad
