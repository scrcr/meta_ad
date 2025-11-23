import os
import pathlib
import requests
from src.interface.image_repository import ImageRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileDownloader(ImageRepository):
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

    def download(self, url: str, dest_path: str) -> str:
        if not url:
            raise ValueError("Missing URL for download")

        full_path = dest_path
        pathlib.Path(os.path.dirname(full_path)).mkdir(parents=True, exist_ok=True)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(full_path, "wb") as file:
            file.write(response.content)
        logger.info("Downloaded snapshot to %s", full_path)
        return full_path
