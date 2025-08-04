import sys
from loguru import logger
from src.database.postgres_database import PostgresDatabase
from src.database.database_factory import get_database_instance
from .db_log_handler import DBLogHandler

def setup_logger(dsn: str = None, component: str = "global") -> None:
    """
    How to use

    ```
from logger_setup import setup_logger
from loguru import logger

setup_logger("dbname=test user=postgres password=postgres host=localhost port=5432", component="video_downloader")

logger.info("Downloader started")
logger.warning("Slow response from server")
logger.error("Failed to download video")
logger.debug("Debug info", extra={"url": "http://example.com"})
    ```
    """
    db = get_database_instance()
    db_handler = DBLogHandler(db, component)

    logger.remove() 
    logger.add(db_handler, level="DEBUG")
    logger.add(sys.stderr, level="INFO")
