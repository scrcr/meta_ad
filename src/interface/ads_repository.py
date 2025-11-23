from abc import ABC, abstractmethod
from typing import List

from src.core.ad import Ad


class AdsRepository(ABC):
    @abstractmethod
    def fetch_recent_ads(self) -> List[Ad]:
        raise NotImplementedError
