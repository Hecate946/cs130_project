from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
from models.gyms import Gym, GymZoneSnapshot, GymHoursSnapshot

logger = logging.getLogger(__name__)

class GymDatabase:
    def __init__(self, db_manager):
        self.db = db_manager
        logger.info("Initialized GymDatabase")

    def get_gym_by_slug(self, slug: str) -> Optional[Gym]:
        """Get gym information by slug"""
        logger.info(f"Getting gym info for slug: {slug}")
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, name, slug, last_updated
                        FROM gyms
                        WHERE slug = %s
                    """, (slug,))
                    row = cur.fetchone()
                    if row:
                        logger.info(f"Found gym with id: {row[0]}, name: {row[1]}")
                        return Gym(*row)
                    logger.warning(f"No gym found with slug: {slug}")
                    return None
        except Exception as e:
            logger.error(f"Error getting gym by slug: {e}")
            return None

    def create_gym_zones_snapshot(self, slug: str, zones_data: List[Dict]) -> bool:
        """Creates a new snapshot of gym zone data"""
        logger.info(f"Creating zones snapshot for gym: {slug}")
        try:
            gym = self.get_gym_by_slug(slug)
            if not gym:
                logger.error(f"No gym found with slug {slug}")
                return False

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Update gym's last_updated timestamp
                    cur.execute("""
                        UPDATE gyms 
                        SET last_updated = NOW() 
                        WHERE id = %s
                    """, (gym.id,))
                    
                    # Create new snapshot
                    cur.execute("""
                        INSERT INTO gym_zones_snapshot 
                        (gym_id, zones)
                        VALUES (%s, %s)
                        RETURNING id
                    """, (
                        gym.id,
                        json.dumps(zones_data)
                    ))
                    snapshot_id = cur.fetchone()[0]
                    logger.info(f"Created zones snapshot with id: {snapshot_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating gym zones snapshot: {e}")
            return False

    def update_gym_hours(self, slug: str, regular_hours: Dict[str, str], special_hours: Optional[Dict[str, str]] = None) -> bool:
        """Creates a new snapshot of gym hours"""
        try:
            gym = self.get_gym_by_slug(slug)
            if not gym:
                logger.error(f"No gym found with slug {slug}")
                return False

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO gym_hours_snapshot 
                        (gym_id, regular_hours, special_hours)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (
                        gym.id,
                        json.dumps(regular_hours),
                        json.dumps(special_hours) if special_hours else None
                    ))
            return True
        except Exception as e:
            logger.error(f"Error updating gym hours: {e}")
            return False

    def get_latest_gym_zones(self, slug: str) -> Optional[GymZoneSnapshot]:
        """Retrieves the most recent gym zone snapshot for a specific gym"""
        try:
            gym = self.get_gym_by_slug(slug)
            if not gym:
                logger.error(f"No gym found with slug {slug}")
                return None

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, gym_id, snapshot_time, zones
                        FROM gym_zones_snapshot
                        WHERE gym_id = %s
                        ORDER BY snapshot_time DESC
                        LIMIT 1
                    """, (gym.id,))
                    row = cur.fetchone()
                    if row:
                        return GymZoneSnapshot(
                            id=row[0],
                            gym_id=row[1],
                            snapshot_time=row[2],
                            zones=row[3]  # psycopg already deserializes JSONB
                        )
                    return None
        except Exception as e:
            logger.error(f"Error getting latest gym zones: {e}")
            return None

    def get_latest_gym_hours(self, slug: str) -> Optional[GymHoursSnapshot]:
        """Retrieves the most recent gym hours snapshot"""
        try:
            gym = self.get_gym_by_slug(slug)
            if not gym:
                logger.error(f"No gym found with slug {slug}")
                return None

            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, gym_id, snapshot_time, regular_hours, special_hours
                        FROM gym_hours_snapshot
                        WHERE gym_id = %s
                        ORDER BY snapshot_time DESC
                        LIMIT 1
                    """, (gym.id,))
                    row = cur.fetchone()
                    if row:
                        return GymHoursSnapshot(
                            id=row[0],
                            gym_id=row[1],
                            snapshot_time=row[2],
                            regular_hours=row[3] or {},  # psycopg already deserializes JSONB
                            special_hours=row[4]  # psycopg already deserializes JSONB
                        )
                    return None
        except Exception as e:
            logger.error(f"Error getting latest gym hours: {e}")
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
            "hours": {
                "regular": hours.regular_hours if hours else {},
                "special": hours.special_hours if hours else None
            } if hours else None,
            "last_updated": zones.snapshot_time.isoformat() if zones else None
        }