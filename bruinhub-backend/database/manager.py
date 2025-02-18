import psycopg
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_connection(self):
        return psycopg.connect(self.db_url)

    def test_connection(self) -> bool:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False 