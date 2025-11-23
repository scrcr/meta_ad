from src.config import PipelineConfig
from src.usecase.run_pipeline import run_pipeline
from src.utils.logger import get_logger


logger = get_logger(__name__)


def main() -> None:
    config = PipelineConfig.from_env()
    run_pipeline(config)


if __name__ == "__main__":
    main()
