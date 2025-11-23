from abc import ABC, abstractmethod
from typing import Iterable, Mapping, MutableMapping


class StorageRepository(ABC):
    @abstractmethod
    async def upsert(self, records: Iterable[Mapping[str, object]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def upsert_page_ids(self, page_ids: Iterable[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> "StorageRepository":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


def normalize_record(record: MutableMapping[str, object]) -> MutableMapping[str, object]:
    return {key: value for key, value in record.items() if value is not None}
