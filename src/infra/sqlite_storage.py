import sqlite3
from pathlib import Path
from typing import Dict, List

from src.core.ad import Ad
from src.interface.storage_repository import StorageRepository


class SQLiteStorage(StorageRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ads (
                ad_id TEXT PRIMARY KEY,
                advertiser TEXT,
                creative_body TEXT,
                call_to_action TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                ad_id TEXT PRIMARY KEY,
                path TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ocr (
                ad_id TEXT PRIMARY KEY,
                text TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                ad_id TEXT,
                tag TEXT
            )
            """
        )
        self.conn.commit()

    def store_ad(self, ad: Ad) -> None:
        self.conn.execute(
            "REPLACE INTO ads (ad_id, advertiser, creative_body, call_to_action) VALUES (?, ?, ?, ?)",
            (ad.ad_id, ad.advertiser, ad.creative_body, ad.call_to_action),
        )

    def store_image(self, ad_id: str, image_path: str) -> None:
        self.conn.execute(
            "REPLACE INTO images (ad_id, path) VALUES (?, ?)", (ad_id, str(image_path))
        )

    def store_ocr(self, ad_id: str, text: str) -> None:
        self.conn.execute("REPLACE INTO ocr (ad_id, text) VALUES (?, ?)", (ad_id, text))

    def store_tags(self, ad_id: str, tags: List[str]) -> None:
        self.conn.execute("DELETE FROM tags WHERE ad_id = ?", (ad_id,))
        self.conn.executemany(
            "INSERT INTO tags (ad_id, tag) VALUES (?, ?)", [(ad_id, tag) for tag in tags]
        )

    def fetch_tag_ranking(self) -> List[Dict[str, object]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT tag, COUNT(*) as cnt FROM tags GROUP BY tag ORDER BY cnt DESC, tag ASC"
        )
        return [{"tag": row[0], "count": row[1]} for row in cur.fetchall()]

    def commit(self) -> None:
        self.conn.commit()

    def __del__(self) -> None:  # pragma: no cover - defensive close
        try:
            self.conn.close()
        except Exception:
            pass
