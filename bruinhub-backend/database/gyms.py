from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from models.gyms import Gym, GymCapacityHistory
from database.manager import DatabaseManager

logger = logging.getLogger(__name__)

class GymDatabase:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        logger.info("Initialized GymDatabase")

    def get_gym_by_slug(self, slug: str) -> Optional[Gym]:
        """Get gym information by slug."""
        logger.info(f"Getting gym info for slug: {slug}")
        
        query = """
            SELECT id, slug, regular_hours, special_hours, last_updated
            FROM gyms
            WHERE slug = %s
        """
        row = self.db.fetch_one(query, (slug,))
        
        if row:
            return Gym(
                id=row[0],
                slug=row[1],
                regular_hours=row[2] if row[2] else {},
                special_hours=row[3] if row[3] else None,
                last_updated=row[4],
            )
        
        logger.warning(f"No gym found with slug: {slug}")
        return None

    def update_gym_hours(
        self, slug: str, regular_hours: Dict[str, str], special_hours: Optional[Dict[str, str]] = None
    ) -> bool:
        """Updates a gym's regular and special hours."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return False

        update_query = """
            UPDATE gyms
            SET regular_hours = %s, special_hours = %s, last_updated = NOW()
            WHERE id = %s
        """
        params = (json.dumps(regular_hours), json.dumps(special_hours) if special_hours else None, gym.id)
        
        self.db.execute(update_query, params)
        logger.info(f"Successfully updated hours for gym: {slug}")
        return True

    def insert_gym_capacity(self, slug: str, zone_name: str, capacity: int) -> bool:
        """Inserts or updates capacity for a specific gym zone."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return False

        insert_query = """
            INSERT INTO gym_capacity_history (gym_id, zone_name, capacity, last_updated)
            VALUES (%s, %s, %s, NOW())
            RETURNING id
        """
        params = (gym.id, zone_name, capacity)
        
        capacity_id = self.db.fetch_one(insert_query, params)
        if capacity_id:
            logger.info(f"Inserted gym capacity entry with ID: {capacity_id[0]}")
            return True

        logger.error("Failed to insert gym capacity")
        return False

    def get_latest_gym_capacity(self, slug: str) -> Optional[List[GymCapacityHistory]]:
        """Retrieves the most recent capacity data for each gym zone."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return None

        query = """
            SELECT id, gym_id, zone_name, capacity, last_updated
            FROM gym_capacity_history
            WHERE gym_id = %s
            ORDER BY last_updated DESC
        """
        rows = self.db.fetch_all(query, (gym.id,))
        
        if rows:
            return [
                GymCapacityHistory(
                    id=row[0],
                    gym_id=row[1],
                    zone_name=row[2],
                    capacity=row[3],
                    last_updated=row[4],
                )
                for row in rows
            ]

        logger.warning(f"No capacity data found for gym: {slug}")
        return None

    def get_gym_latest(self, slug: str) -> Dict:
        """Gets the latest data for a gym, including capacity per zone."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            return {}

        capacities = self.get_latest_gym_capacity(slug)
        zones = {
            cap.zone_name: {"capacity": cap.capacity, "last_updated": cap.last_updated.isoformat()}
            for cap in capacities
        } if capacities else {}

        return {
            "slug": gym.slug,
            "regular_hours": gym.regular_hours,
            "special_hours": gym.special_hours,
            "zones": zones,
            "last_updated": gym.last_updated.isoformat(),
        }
