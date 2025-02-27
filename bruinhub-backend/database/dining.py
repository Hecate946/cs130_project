import logging
from typing import Dict, Optional
from datetime import datetime
from models.dining import db, DiningHall, DiningCapacityHistory
from database.manager import DatabaseManager
from sqlalchemy import func

logger = logging.getLogger(__name__)

class DiningDatabase:
    def __init__(self):
        logger.info("Initialized DiningDatabase")

    def get_dining_hall_by_slug(self, slug: str) -> Optional[DiningHall]:
        """Get dining hall information by slug."""
        logger.info(f"Getting dining hall info for slug: {slug}")
        return DiningHall.query.filter_by(slug=slug).first()

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

        hall.menu = menu
        hall.hours_today = hours_today
        db.session.commit()
        
        logger.info(f"Successfully updated dining hall {slug}")
        return True

    def insert_dining_capacity(self, slug: str, capacity: int) -> bool:
        """Inserts a capacity record for a dining hall."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            logger.error(f"No dining hall found with slug {slug}")
            return False

        new_capacity = DiningCapacityHistory(
            hall_id=hall.id,
            capacity=capacity
        )
        db.session.add(new_capacity)
        db.session.commit()

        logger.info(f"Inserted dining capacity entry with ID: {new_capacity.id}")
        return True

    def get_latest_dining_capacity(self, slug: str) -> Optional[DiningCapacityHistory]:
        """Retrieves the most recent capacity data for a dining hall."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            logger.error(f"No dining hall found with slug {slug}")
            return None

        capacity = DiningCapacityHistory.query.filter_by(
            hall_id=hall.id
        ).order_by(
            DiningCapacityHistory.last_updated.desc()
        ).first()

        if not capacity:
            logger.warning(f"No capacity data found for dining hall: {slug}")
            return None

        return capacity

    def get_dining_hall_latest(self, slug: str) -> Dict:
        """Gets the latest data for a dining hall, including capacity."""
        hall = self.get_dining_hall_by_slug(slug)
        if not hall:
            return {}

        capacity = self.get_latest_dining_capacity(slug)
        return {
            "slug": hall.slug,
            "capacity": capacity.capacity if capacity else None,
            "menu": hall.menu,
            "hours_today": hall.hours_today,
            "occupants": capacity.occupants if capacity else 0,
            "capacity": capacity.capacity if capacity else 0,
            "last_updated": hall.last_updated.isoformat(),
        }
