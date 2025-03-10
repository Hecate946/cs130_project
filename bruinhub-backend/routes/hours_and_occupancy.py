import logging
from datetime import datetime

from config import FACILITY_IDS, OCCUSPACE_IDS
from database.dining import DiningDatabase
from database.gyms import GymDatabase
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

hours_route = Blueprint("hours_route", __name__)
dining_db = DiningDatabase()
gym_db = GymDatabase()


@hours_route.route("/v1/hours-and-occupancy", methods=["GET"])
def get_hours():
    """
    Gets hours and occupancy for all facilities, currently that is only dining halls and gyms.

    Example:
    - `/v1/hours` → Returns list of hours and occupancy for each facility that has them
    """
    data = {}

    logger.info("Fetching hours and occupancy for dining halls")
    for slug in OCCUSPACE_IDS:
        hall_occupancy = dining_db.get_latest_dining_capacity(slug)
        hall_data = dining_db.get_dining_hall_latest(slug)
        
        if hall_data and "hours_today" in hall_data:
            hall_hours = hall_data["hours_today"]
            if hall_occupancy:
                data[slug] = {
                    "hours": hall_hours,
                    "occupants": hall_occupancy.occupants,
                    "capacity": hall_occupancy.capacity,
                }
            else:
                continue  # Skip this dining hall if no occupancy data
        else:
            continue  # Skip this dining hall if no hours data

    logger.info("Fetching hours and occupancy for gyms")
    for slug in FACILITY_IDS:
        gym_data = gym_db.get_gym_latest(slug)
        
        if gym_data and "regular_hours" in gym_data:
            gym_hours = gym_data["regular_hours"]
            if "capacity" in gym_data and "occupants" in gym_data:
                data[slug] = {
                    "hours": gym_hours,
                    "occupants": gym_data["occupants"],
                    "capacity": gym_data["capacity"]
                }
            else:
                continue  # Skip this gym if no occupancy data
        else:
            continue  # Skip this gym if no hours data

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})
