import os
from dotenv import load_dotenv
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import execute_values
from .base_database import BaseDatabase
from contextlib import contextmanager

from typing import Optional, Any, List, Tuple

load_dotenv()

class PostgresDatabase(BaseDatabase):
    def __init__(self, dsn: Optional[str] = None, minconn: int = 1, maxconn: int = 10):
        load_dotenv()
        if dsn is None:
            dsn = os.environ.get("POSTGRES_DSN")

        if not dsn:
            raise ValueError("DSN is not provided and POSTGRES_DSN not found in environment variables.")

        self.pool = SimpleConnectionPool(minconn, maxconn, dsn=dsn)
        if not self.pool:
            raise Exception("Failed to create connection pool")
        
    @contextmanager
    def get_connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:
                    return cur.fetchall()
                conn.commit()
                return None

    def execute_many(self, query: str, params_list: List[Tuple]) -> Any:
        """
        Eksekusi batch insert/update menggunakan execute_values.
        Pastikan query format-nya menggunakan %s, bukan ($1, $2, ...).
        Contoh:
            INSERT INTO table_name (col1, col2) VALUES %s
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                execute_values(cur, query, params_list)
                conn.commit()

    def health_check(self) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result[0] == 1
        except Exception as e:
            return False
