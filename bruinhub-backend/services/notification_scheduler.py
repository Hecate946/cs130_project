"""Service for scheduling and sending capacity notifications."""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import func
from models.notifications import DeviceToken
from models.dining import DiningHall, DiningCapacityHistory
from models.gyms import Gym, GymCapacityHistory
from services.notification_service import NotificationService
from config.facility_names import FACILITY_NAMES
from database.db import db

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Handles periodic checking of facility capacities and sending notifications."""

    @staticmethod
    def _calculate_gym_capacity(gym_id: int) -> Optional[Tuple[int, int]]:
        """
        Calculate the total occupants and capacity for a gym across all zones.

        Args:
            gym_id: The ID of the gym

        Returns:
            Tuple of (total_occupants, total_capacity) if data exists, None otherwise
        """
        # Get the latest capacity records for each zone
        latest_zone_records = (
            db.session.query(
                GymCapacityHistory.zone_name,
                GymCapacityHistory.gym_id,
                func.max(GymCapacityHistory.last_updated).label("max_date"),
            )
            .filter(GymCapacityHistory.gym_id == gym_id)
            .group_by(GymCapacityHistory.zone_name, GymCapacityHistory.gym_id)
            .subquery()
        )

        # Join to get the full records
        latest_capacities = GymCapacityHistory.query.join(
            latest_zone_records,
            db.and_(
                GymCapacityHistory.zone_name == latest_zone_records.c.zone_name,
                GymCapacityHistory.last_updated == latest_zone_records.c.max_date,
                GymCapacityHistory.gym_id == latest_zone_records.c.gym_id,
            ),
        ).all()

        if not latest_capacities:
            return None

        total_occupants = sum(cap.occupants for cap in latest_capacities)
        total_capacity = sum(cap.capacity for cap in latest_capacities)

        return (total_occupants, total_capacity)

    @staticmethod
    def check_and_notify():
        """
        Check all facility capacities and send notifications to eligible devices.
        This should be run every 5 minutes.
        """
        logger.info("Starting capacity check for notifications")

        try:
            # Get all active devices
            devices = DeviceToken.query.filter_by(is_active=True).all()
            if not devices:
                logger.info("No active devices found")
                return

            # Check dining halls
            dining_halls = DiningHall.query.all()
            for hall in dining_halls:
                # Get latest capacity
                latest_capacity = (
                    DiningCapacityHistory.query.filter_by(hall_id=hall.id)
                    .order_by(DiningCapacityHistory.last_updated.desc())
                    .first()
                )

                if latest_capacity:
                    capacity_percentage = (
                        latest_capacity.occupants / latest_capacity.capacity
                    ) * 100
                    facility_name = FACILITY_NAMES.get(hall.slug, hall.slug)

                    # Check each device's preferences
                    for device in devices:
                        preferences = device.preferences.get("capacity", {}).get(
                            hall.slug, {}
                        )
                        if preferences.get("enabled", False):
                            threshold = preferences.get("threshold", 50)

                            # Send notification if capacity is below threshold
                            if capacity_percentage >= threshold:
                                NotificationService.dispatch_notification(
                                    push_token=device.push_token,
                                    title=f"{facility_name} Capacity Alert",
                                    message=f"{facility_name} is at {int(capacity_percentage)}% capacity",
                                    data={
                                        "type": "capacity",
                                        "facility": hall.slug,
                                        "capacity": capacity_percentage,
                                    },
                                )

            # Check gyms
            gyms = Gym.query.all()
            for gym in gyms:
                # Calculate aggregate capacity
                capacity_data = NotificationScheduler._calculate_gym_capacity(gym.id)

                if capacity_data:
                    total_occupants, total_capacity = capacity_data
                    capacity_percentage = (total_occupants / total_capacity) * 100
                    facility_name = FACILITY_NAMES.get(gym.slug, gym.slug)

                    # Check each device's preferences
                    for device in devices:
                        preferences = device.preferences.get("capacity", {}).get(
                            gym.slug, {}
                        )
                        if preferences.get("enabled", False):
                            threshold = preferences.get("threshold", 50)

                            # Send notification if capacity exceeds threshold
                            if capacity_percentage >= threshold:
                                NotificationService.dispatch_notification(
                                    push_token=device.push_token,
                                    title=f"{facility_name} Capacity Alert",
                                    message=f"{facility_name} is at {int(capacity_percentage)}% capacity",
                                    data={
                                        "type": "capacity",
                                        "facility": gym.slug,
                                        "capacity": capacity_percentage,
                                    },
                                )

            logger.info("Completed capacity check for notifications")

        except Exception as e:
            logger.error(
                f"Error checking capacities for notifications: {str(e)}", exc_info=True
            )
