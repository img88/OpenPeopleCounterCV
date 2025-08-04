import os
from dotenv import load_dotenv
from .postgres_database import PostgresDatabase
from .base_database import BaseDatabase

def get_database_instance() -> BaseDatabase:
    load_dotenv()

    provider = os.environ.get("DATABASE_PROVIDER", "").upper()
    
    if provider == "POSTGRES":
        dsn = os.environ.get("POSTGRES_DSN")
        if not dsn:
            raise ValueError("POSTGRES_DSN is not set in environment")
        return PostgresDatabase(dsn=dsn)

    else:
        raise ValueError(f"Unsupported DATABASE_PROVIDER: {provider}")
