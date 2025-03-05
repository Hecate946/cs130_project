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
        occupants: int,
        capacity: int,
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
            occupants=occupants,
            capacity=capacity,
            last_updated=last_updated
        ).first()

        if not existing:
            new_capacity = GymCapacityHistory(
                gym_id=gym.id,
                zone_name=zone_name,
                occupants=occupants,
                capacity=capacity,
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
            GymCapacityHistory.gym_id,
            db.func.max(GymCapacityHistory.last_updated).label('max_date')
        ).group_by(GymCapacityHistory.zone_name, GymCapacityHistory.gym_id).subquery()

        # Query to get the full capacity records
        capacities = GymCapacityHistory.query.join(
            latest_capacities,
            db.and_(
                GymCapacityHistory.zone_name == latest_capacities.c.zone_name,
                GymCapacityHistory.last_updated == latest_capacities.c.max_date,
                GymCapacityHistory.gym_id == latest_capacities.c.gym_id
            )
        ).filter(GymCapacityHistory.gym_id == gym.id).order_by(GymCapacityHistory.zone_name).all()

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
                "occupants": cap.occupants,
                "capacity": cap.capacity,
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

    def get_historical_capacity(self, slug: str) -> Dict[str, Dict[int, Dict[str, float]]]:
        """
        Calculate historical capacity averages by hour for each zone in a gym.
        
        Returns:
            Dict[str, Dict[int, Dict[str, float]]]: A dictionary mapping zone names to their hourly averages:
            {
                "Weight Room": {
                    6: {"occupants": 30.5, "capacity": 50.0},
                    7: {"occupants": 45.2, "capacity": 50.0},
                    ...
                },
                "Cardio Room": {
                    6: {"occupants": 20.3, "capacity": 40.0},
                    ...
                }
            }
            Hours with no data will return {"occupants": 0.0, "capacity": 0.0}
        """
        gym = self.get_gym_by_slug(slug)
        if not gym:
            return {}

        # Get all capacity records for this gym
        capacities = GymCapacityHistory.query.filter_by(
            gym_id=gym.id
        ).order_by(
            GymCapacityHistory.last_updated
        ).all()

        if not capacities:
            return {}

        # Initialize data structure
        zone_data = {}

        # Group capacities by zone
        for capacity in capacities:
            zone_name = capacity.zone_name
            if zone_name not in zone_data:
                # Initialize hourly counters for this zone
                zone_data[zone_name] = {
                    hour: {"occupants": 0.0, "capacity": 0.0, "count": 0}
                    for hour in range(6, 26)  # 6am to 1am
                }

            hour = capacity.last_updated.hour
            if hour in zone_data[zone_name]:
                zone_data[zone_name][hour]["occupants"] += capacity.occupants
                zone_data[zone_name][hour]["capacity"] += capacity.capacity
                zone_data[zone_name][hour]["count"] += 1

        # Calculate averages for each zone, return 0 for hours with no data
        result = {}
        for zone_name, hourly_data in zone_data.items():
            result[zone_name] = {}
            for hour, data in hourly_data.items():
                if data["count"] > 0:
                    result[zone_name][hour] = {
                        "occupants": round(data["occupants"] / data["count"], 1),
                        "capacity": round(data["capacity"] / data["count"], 1)
                    }
                else:
                    result[zone_name][hour] = {"occupants": 0.0, "capacity": 0.0}

        return result
