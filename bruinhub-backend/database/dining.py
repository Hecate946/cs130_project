import logging
import json
from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


class DiningDatabase:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        logger.info("Initialized DiningDatabase")

    def get_all_dining_halls(self):
        """
        Retrieves all dining halls and their menu items.
        This should be replaced with an actual database query.
        """
        logger.info("Fetching all dining halls from database")

        query = """
        SELECT name, station, menu_items, capacity
        FROM dining_halls
        LEFT JOIN dining_menus ON dining_halls.id = dining_menus.hall_id
        """

        try:
            rows = self.db_manager.fetch_all(query)
            if not rows:
                logger.warning("No dining hall data found in the database")
                return {}

            dining_halls = {}
            for row in rows:
                hall_name = row["name"]
                station = row["station"]
                items = row["menu_items"].split(", ") if row["menu_items"] else []

                if hall_name not in dining_halls:
                    dining_halls[hall_name] = {"capacity": row["capacity"]}

                dining_halls[hall_name][station] = items

            logger.info(
                f"Successfully fetched dining hall data: {len(dining_halls)} halls found"
            )
            return dining_halls

        except Exception as e:
            logger.error(f"Error fetching dining hall data: {e}", exc_info=True)
            return {}


    def create_menu_snapshot(self, hall_name: str, hall_data: Dict):
        """
        Stores a new snapshot of the dining hall's menu.
        """
        logger.info(f"Creating menu snapshot for {hall_name}")

        try:
            # Get the dining hall ID
            query_hall_id = "SELECT id FROM dining_halls WHERE name = %s"
            hall_id = self.db_manager.fetch_one(query_hall_id, (hall_name,))

            if not hall_id:
                logger.error(f"Dining hall {hall_name} not found in database")
                return False

            hall_id = hall_id[0]

            # Convert menu dictionary to JSON string
            hall_data_json = json.dumps(hall_data)

            # Insert menu snapshot
            insert_query = """
                INSERT INTO dining_menu_snapshot (hall_id, snapshot_time, menu)
                VALUES (%s, NOW(), %s)
            """
            self.db_manager.execute(insert_query, (hall_id, hall_data_json))
            logger.info(f"Successfully stored menu snapshot for {hall_name}")
            return True

        except Exception as e:
            logger.error(
                f"Error storing menu snapshot for {hall_name}: {e}", exc_info=True
            )
            return False


    def update_dining_hours(self, hall_name: str, regular_hours: dict, special_hours: Optional[dict] = None):
        """Stores a new snapshot of dining hall hours."""
        logger.info(f"Updating hours snapshot for {hall_name}")

        try:
            # Get the dining hall ID
            query_hall_id = "SELECT id FROM dining_halls WHERE name = %s"
            hall_id = self.db_manager.fetch_one(query_hall_id, (hall_name,))

            if not hall_id:
                logger.error(f"Dining hall {hall_name} not found in database")
                return False

            hall_id = hall_id[0]

            # Convert dictionaries to JSON strings before inserting into JSONB columns
            regular_hours_json = json.dumps(regular_hours)
            special_hours_json = json.dumps(special_hours) if special_hours else None

            # Insert hours snapshot
            insert_query = """
                INSERT INTO dining_hours_snapshot (hall_id, snapshot_time, regular_hours, special_hours)
                VALUES (%s, NOW(), %s, %s)
            """
            self.db_manager.execute(insert_query, (hall_id, regular_hours_json, special_hours_json))
            logger.info(f"Successfully stored hours snapshot for {hall_name}")
            return True

        except Exception as e:
            logger.error(f"Error updating hours for {hall_name}: {e}", exc_info=True)
            return False
