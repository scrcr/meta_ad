from dotenv import load_dotenv

from src.config import PipelineConfig
from src.usecase.run_pipeline import run_pipeline
from src.utils.logger import get_logger


logger = get_logger(__name__)


def main() -> None:
    load_dotenv()
    config = PipelineConfig.from_env()
    if config.storage.supabase_url:
        logger.info("Supabase URL loaded: %s...", config.storage.supabase_url[:10])
    else:
        logger.warning("Supabase URL NOT loaded")
    run_pipeline(config)


if __name__ == "__main__":
    main()
