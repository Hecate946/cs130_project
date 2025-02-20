from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from models.gyms import Gym, GymZoneSnapshot, GymHoursSnapshot
from database.manager import DatabaseManager

logger = logging.getLogger(__name__)

class GymDatabase:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        logger.info("Initialized GymDatabase")

    def get_gym_by_slug(self, slug: str) -> Optional[Gym]:
        """Get gym information by slug"""
        logger.info(f"Getting gym info for slug: {slug}")
        
        query = """
            SELECT id, name, slug, last_updated
            FROM gyms
            WHERE slug = %s
        """
        row = self.db.fetch_one(query, (slug,))
        
        if row:
            logger.info(f"Found gym with id: {row[0]}, name: {row[1]}")
            return Gym(*row)
        
        logger.warning(f"No gym found with slug: {slug}")
        return None

    def create_gym_zones_snapshot(self, slug: str, zones_data: List[Dict]) -> bool:
        """Creates a new snapshot of gym zone data"""
        logger.info(f"Creating zones snapshot for gym: {slug}")
        
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return False

        # Update gym's last_updated timestamp
        update_query = """
            UPDATE gyms 
            SET last_updated = NOW() 
            WHERE id = %s
        """
        self.db.execute(update_query, (gym.id,))

        # Insert new snapshot
        insert_query = """
            INSERT INTO gym_zones_snapshot 
            (gym_id, zones)
            VALUES (%s, %s)
            RETURNING id
        """
        snapshot_id = self.db.fetch_one(insert_query, (gym.id, json.dumps(zones_data)))

        if snapshot_id:
            logger.info(f"Created zones snapshot with id: {snapshot_id[0]}")
            return True

        logger.error("Failed to create gym zones snapshot")
        return False

    def update_gym_hours(
        self,
        slug: str,
        regular_hours: Dict[str, str],
        special_hours: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Creates a new snapshot of gym hours"""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return False

        insert_query = """
            INSERT INTO gym_hours_snapshot 
            (gym_id, regular_hours, special_hours)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        params = (gym.id, json.dumps(regular_hours), json.dumps(special_hours) if special_hours else None)
        
        snapshot_id = self.db.fetch_one(insert_query, params)

        if snapshot_id:
            logger.info(f"Successfully stored gym hours snapshot with id: {snapshot_id[0]}")
            return True

        logger.error("Failed to update gym hours snapshot")
        return False

    def get_latest_gym_zones(self, slug: str) -> Optional[GymZoneSnapshot]:
        """Retrieves the most recent gym zone snapshot for a specific gym"""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return None

        query = """
            SELECT id, gym_id, snapshot_time, zones
            FROM gym_zones_snapshot
            WHERE gym_id = %s
            ORDER BY snapshot_time DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (gym.id,))
        
        if row:
            return GymZoneSnapshot(
                id=row[0],
                gym_id=row[1],
                snapshot_time=row[2],
                zones=row[3],  # psycopg already deserializes JSONB
            )
        
        return None

    def get_latest_gym_hours(self, slug: str) -> Optional[GymHoursSnapshot]:
        """Retrieves the most recent gym hours snapshot"""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return None

        query = """
            SELECT id, gym_id, snapshot_time, regular_hours, special_hours
            FROM gym_hours_snapshot
            WHERE gym_id = %s
            ORDER BY snapshot_time DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (gym.id,))
        
        if row:
            return GymHoursSnapshot(
                id=row[0],
                gym_id=row[1],
                snapshot_time=row[2],
                regular_hours=row[3] or {},
                special_hours=row[4],  # psycopg already deserializes JSONB
            )
        
        return None

    def get_gym_latest(self, slug: str) -> Dict:
        """Get latest data for a gym by slug"""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            return {}

        zones = self.get_latest_gym_zones(slug)
        hours = self.get_latest_gym_hours(slug)

        return {
            "name": gym.name,
            "slug": gym.slug,
            "zones": zones.zones if zones else [],
            "hours": (
                {
                    "regular": hours.regular_hours if hours else {},
                    "special": hours.special_hours if hours else None,
                }
                if hours
                else None
            ),
            "last_updated": zones.snapshot_time.isoformat() if zones else None,
        }
