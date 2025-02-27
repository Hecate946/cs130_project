import psycopg
import logging
from typing import Optional, Tuple, List, Any

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_url: str):
        self.db_url = db_url
        if not self.db_url:
            raise ValueError("DATABASE_URL is not set!")
        logger.info(f"Connecting to database: {self.db_url}")

        # Switched to ORM so don't run schema
        # self.run_schema()
        # logger.info("Database schema updated.")

    def run_schema(self):
        """Runs the schemas.sql script at startup."""
        try:
            logger.info(
                "Applying database schema from database/schemas.sql...")
            conn = psycopg.connect(self.db_url)
            cur = conn.cursor()

            with open("database/schemas.sql", "r") as schema_file:
                schema_sql = schema_file.read()
                cur.execute(schema_sql)

            conn.commit()
            logger.info("Database schema applied successfully.")

            cur.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error applying database schema: {e}", exc_info=True)

    def get_connection(self):
        """Establishes a new database connection."""
        return psycopg.connect(self.db_url)

    def test_connection(self) -> bool:
        """Tests if the database connection is working."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def execute(self, query: str, params: Tuple[Any, ...] = ()):
        """Executes a query without returning results (INSERT, UPDATE, DELETE)."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    conn.commit()
                    logger.info("Query executed successfully.")
        except Exception as e:
            logger.error(
                f"Error executing query: {query} with params {params}: {e}",
                exc_info=True,
            )

    def fetch_one(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> Optional[Tuple[Any, ...]]:
        """Executes a query and fetches a single row."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    return cur.fetchone()
        except Exception as e:
            logger.error(
                f"Error fetching one row: {query} with params {params}: {e}",
                exc_info=True,
            )
            return None

    def fetch_all(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> List[Tuple[Any, ...]]:
        """Executes a query and fetches all results."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    return cur.fetchall()
        except Exception as e:
            logger.error(
                f"Error fetching all rows: {query} with params {params}: {e}",
                exc_info=True,
            )
            return []
