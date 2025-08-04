from fastapi import FastAPI
from src.logging.logger_setup import setup_logger
from loguru import logger

from src.downloader.route import router as download_route
from src.region.route import router as region_router
from src.downloader.route import router as download_crud_route
from src.database.database_factory import get_database_instance

# Setup logging table
db = get_database_instance()
with open("src/ddl/ddl_logging.sql", "r", encoding="utf-8") as file:
    query = file.read()
    db.execute_query(query)

setup_logger(component="main")

# Setup all table
logger.info("SETUP starting...")

ddls = [
    "src/ddl/ddl_video.sql",
    "src/ddl/ddl_region.sql"
]

for ddl in ddls:
    try:
        with open(ddl, "r", encoding="utf-8") as file:
            query = file.read()
            db.execute_query(query)
            logger.info(f"DDL: {ddl}")
    except Exception as e:
        msg = f"Error while setup database: {e}"
        logger.error(msg)
        raise Exception(msg)

logger.info("SETUP finished")

app = FastAPI()

app.include_router(download_route)
app.include_router(region_router)
app.include_router(download_crud_route)