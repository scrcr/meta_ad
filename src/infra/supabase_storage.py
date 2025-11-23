import asyncio
import json
from typing import Iterable, Mapping
import requests

from src.config import StorageConfig
from src.interface.storage_repository import StorageRepository, normalize_record
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseStorage(StorageRepository):
    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        if not (config.supabase_url and config.supabase_key):
            logger.warning("Supabase credentials missing; persistence will be skipped.")
        self._session = requests.Session()

    async def upsert(self, records: Iterable[Mapping[str, object]]) -> None:
        if not (self.config.supabase_url and self.config.supabase_key):
            logger.info("Skipping Supabase upsert due to missing configuration")
            return
        await self._upsert_to_table(self.config.table, records)

    async def upsert_page_ids(self, page_ids: Iterable[str]) -> None:
        if not (self.config.supabase_url and self.config.supabase_key):
            logger.info("Skipping Supabase page_id upsert due to missing configuration")
            return
        records = ({"page_id": page_id} for page_id in page_ids)
        await self._upsert_to_table(self.config.page_table, records)

    async def close(self) -> None:
        self._session.close()

    async def _upsert_to_table(self, table: str, records: Iterable[Mapping[str, object]]) -> None:
        url = f"{self.config.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.config.supabase_key,
            "Authorization": f"Bearer {self.config.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }

        payload = [normalize_record(dict(record)) for record in records]
        if not payload:
            return

        def _post() -> None:
            response = self._session.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status()

        await asyncio.to_thread(_post)
        logger.info("Upserted %s records into Supabase table %s", len(payload), table)
