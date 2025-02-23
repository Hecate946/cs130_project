import logging
import json
from typing import Dict, Optional
from models.dining import DiningHall, DiningCapacityHistory
from database.manager import DatabaseManager

logger = logging.getLogger(__name__)


class DiningDatabase:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        logger.info("Initialized DiningDatabase")

    def get_dining_hall_by_slug(self, slug: str) -> Optional[DiningHall]:
        """Get dining hall information by slug."""
        logger.info(f"Getting dining hall info for slug: {slug}")

        query = """
            SELECT id, slug, menu, hours_today, last_updated
            FROM dining_halls
            WHERE slug = %s
        """
        row = self.db_manager.fetch_one(query, (slug,))

        if row:
            return DiningHall(
                id=row[0],
                slug=row[1],
                menu=row[2] if row[2] else {},
                hours_today=row[3] if row[3] else {},
                last_updated=row[4],
            )

        logger.warning(f"No dining hall found with slug: {slug}")
        return None

    def update_dining_hall(
        self,
        slug: str,
        menu: Dict[str, list],
        hours_today: Dict[str, str],
    ) -> bool:
        """Updates a dining hall's menu and hours."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            logger.error(f"No dining hall found with slug {slug}")
            return False

        update_query = """
            UPDATE dining_halls
            SET menu = %s, hours_today = %s, last_updated = NOW()
            WHERE slug = %s
        """
        params = (
            json.dumps(menu),
            json.dumps(hours_today),
            slug,
        )

        self.db_manager.execute(update_query, params)
        logger.info(f"Successfully updated dining hall {slug}")
        return True

    def insert_dining_capacity(self, slug: str, occupants: int, capacity: int) -> bool:
        """Inserts a capacity and occupancy record for a dining hall."""
        try:
            insert_query = """
                INSERT INTO dining_capacity_history (slug, occupants, capacity, last_updated)
                VALUES (%s, %s, %s, NOW())
                RETURNING id
            """
            params = (slug, occupants, capacity)

            capacity_id = self.db_manager.fetch_one(insert_query, params)
            if capacity_id:
                logger.info(f"Inserted dining capacity entry with ID: {capacity_id[0]}")
                return True

            logger.error("Failed to insert dining capacity")
            return False
        except Exception as e:
            logger.error(f"Error inserting dining capacity: {e}")
            return False

    def get_latest_dining_capacity(self, slug: str) -> Optional[DiningCapacityHistory]:
        """Retrieves the most recent capacity data for a dining hall."""
        query = """
            SELECT id, slug, occupants, capacity, last_updated
            FROM dining_capacity_history
            WHERE slug = %s
            ORDER BY last_updated DESC
            LIMIT 1
        """
        row = self.db_manager.fetch_one(query, (slug,))

        if row:
            return DiningCapacityHistory(
                id=row[0],
                slug=row[1],
                occupants=row[2],
                capacity=row[3],
                last_updated=row[4],
            )

        logger.warning(f"No capacity data found for dining hall: {slug}")
        return None

    def get_dining_hall_latest(self, slug: str) -> Dict:
        """Gets the latest data for a dining hall, including capacity."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            return {}

        capacity = self.get_latest_dining_capacity(slug)
        return {
            "slug": hall.slug,
            "menu": hall.menu,
            "hours_today": hall.hours_today,
            "occupants": capacity.occupants if capacity else 0,
            "capacity": capacity.capacity if capacity else 0,
            "last_updated": hall.last_updated.isoformat(),
        }
