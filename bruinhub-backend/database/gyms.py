from typing import Dict, List, Optional
import logging
from datetime import datetime
from sqlalchemy import desc
from models.gyms import db, Gym, GymCapacityHistory

logger = logging.getLogger(__name__)

class GymDatabase:
    def __init__(self):
        logger.info("Initialized GymDatabase")

    def get_gym_by_slug(self, slug: str) -> Optional[Gym]:
        """Get gym information by slug."""
        logger.info(f"Getting gym info for slug: {slug}")
        return Gym.query.filter_by(slug=slug).first()

    def update_gym_hours(
        self,
        slug: str,
        regular_hours: Dict[str, str],
        special_hours: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Updates a gym's regular and special hours."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return False

        gym.regular_hours = regular_hours
        gym.special_hours = special_hours
        db.session.commit()
        
        logger.info(f"Successfully updated hours for gym: {slug}")
        return True

    def insert_gym_capacity(
        self,
        slug: str,
        zone_name: str,
        capacity: int,
        percentage: int,
        last_updated: str,
    ) -> bool:
        """Inserts or updates capacity for a specific gym zone."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return False

        # Check for existing identical entry
        existing = GymCapacityHistory.query.filter_by(
            gym_id=gym.id,
            zone_name=zone_name,
            capacity=capacity,
            percentage=percentage,
            last_updated=last_updated
        ).first()

        if not existing:
            new_capacity = GymCapacityHistory(
                gym_id=gym.id,
                zone_name=zone_name,
                capacity=capacity,
                percentage=percentage,
                last_updated=last_updated
            )
            db.session.add(new_capacity)
            db.session.commit()
            logger.info(f"Inserted gym capacity entry for {slug} - {zone_name}")
        else:
            logger.info(f"Skipped duplicate capacity entry for {slug} - {zone_name}")
        
        return True

    def get_latest_gym_capacity(self, slug: str) -> Optional[List[GymCapacityHistory]]:
        """Retrieves the most recent capacity data for each gym zone."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            logger.error(f"No gym found with slug {slug}")
            return None

        # Subquery to get the latest capacity for each zone
        latest_capacities = db.session.query(
            GymCapacityHistory.zone_name,
            db.func.max(GymCapacityHistory.last_updated).label('max_date')
        ).filter_by(gym_id=gym.id).group_by(GymCapacityHistory.zone_name).subquery()

        # Query to get the full capacity records
        capacities = GymCapacityHistory.query.join(
            latest_capacities,
            db.and_(
                GymCapacityHistory.zone_name == latest_capacities.c.zone_name,
                GymCapacityHistory.last_updated == latest_capacities.c.max_date
            )
        ).filter_by(gym_id=gym.id).order_by(GymCapacityHistory.zone_name).all()

        if not capacities:
            logger.warning(f"No capacity data found for gym: {slug}")
            return None

        return capacities

    def get_gym_latest(self, slug: str) -> Dict:
        """Gets the latest data for a gym, including capacity per zone."""
        gym = self.get_gym_by_slug(slug)
        if not gym:
            return {}

        capacities = self.get_latest_gym_capacity(slug)
        zones = {
            cap.zone_name: {
                "capacity": cap.capacity,
                "percentage": cap.percentage,
                "last_updated": cap.last_updated.isoformat(),
            }
            for cap in capacities
        } if capacities else {}

        return {
            "slug": gym.slug,
            "regular_hours": gym.regular_hours,
            "special_hours": gym.special_hours,
            "zones": zones,
            "last_updated": gym.last_updated.isoformat(),
        }
