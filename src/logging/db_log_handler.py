from loguru import logger
from typing import Optional, Dict, Any
from datetime import datetime
from psycopg2.extras import Json

from ..database.base_database import BaseDatabase

class DBLogHandler:
    def __init__(self, db: BaseDatabase, component_name: str):
        self.db = db
        self.component = component_name

    def __call__(self, log):
        record = log.record
        try:
            query = """
                INSERT INTO system_log (timestamp, level, component, message, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                datetime.fromtimestamp(record["time"].timestamp()),
                record["level"].name,
                self.component,
                record["message"],
                Json(record["extra"]) if record["extra"] else None
            )
            self.db.execute_query(query, params)
        except Exception as e:
            print("Failed to write log to DB:", e)
