import logging
from typing import Optional

_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str) -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s %(name)s - %(message)s",
        )
        _LOGGER = logging.getLogger("meta_ad")
    return _LOGGER.getChild(name)
