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

