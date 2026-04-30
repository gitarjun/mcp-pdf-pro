import logging
from logging.handlers import RotatingFileHandler

from . import config


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    log_path = config.APP_DIR / "server.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                log_path, maxBytes=1_048_576, backupCount=3, encoding="utf-8"
            ),
        ],
    )
