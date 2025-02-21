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
            SELECT id, slug, menu, regular_hours, special_hours, last_updated
            FROM dining_halls
            WHERE slug = %s
        """
        row = self.db_manager.fetch_one(query, (slug,))

        if row:
            return DiningHall(
                id=row[0],
                slug=row[1],
                menu=row[2] if row[2] else {},
                regular_hours=row[3] if row[3] else {},
                special_hours=row[4] if row[4] else None,
                last_updated=row[5],
            )

        logger.warning(f"No dining hall found with slug: {slug}")
        return None

    def update_dining_hall(
        self,
        slug: str,
        menu: Dict[str, list],
        regular_hours: Dict[str, str],
        special_hours: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Updates a dining hall's menu and hours."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            logger.error(f"No dining hall found with slug {slug}")
            return False

        update_query = """
            UPDATE dining_halls
            SET menu = %s, regular_hours = %s, special_hours = %s, last_updated = NOW()
            WHERE id = %s
        """
        params = (
            json.dumps(menu),
            json.dumps(regular_hours),
            json.dumps(special_hours) if special_hours else None,
            hall.id,
        )

        self.db_manager.execute(update_query, params)
        logger.info(f"Successfully updated dining hall {slug}")
        return True

    def insert_dining_capacity(self, slug: str, capacity: int) -> bool:
        """Inserts a capacity record for a dining hall."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            logger.error(f"No dining hall found with slug {slug}")
            return False

        insert_query = """
            INSERT INTO dining_capacity_history (hall_id, capacity, last_updated)
            VALUES (%s, %s, NOW())
            RETURNING id
        """
        params = (hall.id, capacity)

        capacity_id = self.db_manager.fetch_one(insert_query, params)
        if capacity_id:
            logger.info(
                f"Inserted dining capacity entry with ID: {capacity_id[0]}")
            return True

        logger.error("Failed to insert dining capacity")
        return False

    def get_latest_dining_capacity(self, slug: str) -> Optional[DiningCapacityHistory]:
        """Retrieves the most recent capacity data for a dining hall."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            logger.error(f"No dining hall found with slug {slug}")
            return None

        query = """
            SELECT id, hall_id, capacity, last_updated
            FROM dining_capacity_history
            WHERE hall_id = %s
            ORDER BY last_updated DESC
            LIMIT 1
        """
        row = self.db_manager.fetch_one(query, (hall.id,))

        if row:
            return DiningCapacityHistory(
                id=row[0],
                hall_id=row[1],
                capacity=row[2],
                last_updated=row[3],
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
            "capacity": capacity.capacity if capacity else hall.capacity,
            "menu": hall.menu,
            "regular_hours": hall.regular_hours,
            "special_hours": hall.special_hours,
            "last_updated": hall.last_updated.isoformat(),
        }
