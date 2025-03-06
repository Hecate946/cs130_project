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
    Gets hours  and occupancy for all facilities, currently that is only dining halls and gyms.

    Example:
    - `/v1/hours` → Returns list of hours and occupancy for each facility that has them
    """
    data = {}

    logger.info("Fetching hours and occupancy for dining halls")
    for slug in OCCUSPACE_IDS:
        hall_occupancy = dining_db.get_latest_dining_capacity(slug)
        hall_hours = dining_db.get_dining_hall_latest(slug)["hours_today"]
        if hall_occupancy:
            data[slug] = {
                "hours": hall_hours,
                "occupants": hall_occupancy.occupants,
                "capacity": hall_occupancy.capacity,
            }
        else:
            return jsonify(
                {
                    "error": f"Cannot find hours and occupancy data for dining hall {slug}",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 404

    logger.info("Fetching hours and occupancy for gyms")
    for slug in FACILITY_IDS:
        gym_occupancy = gym_db.get_latest_gym_capacity(slug)
        gym_hours = gym_db.get_gym_latest(slug)["regular_hours"]
        if gym_occupancy:
            data[slug] = {"hours": gym_hours}
            data[slug].update(
                {
                    zone.zone_name: {
                        "occupants": zone.occupants,
                        "capacity": zone.capacity,
                    }
                    for zone in gym_occupancy
                }
            )
        else:
            return jsonify(
                {
                    "error": f"Cannot find hours and occupancy data for gym {slug}",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})
