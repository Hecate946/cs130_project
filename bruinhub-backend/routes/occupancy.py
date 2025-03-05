import logging
from datetime import datetime

from config import FACILITY_IDS, OCCUSPACE_IDS
from database.dining import DiningDatabase
from database.gyms import GymDatabase
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

occupancy_routes = Blueprint("occupancy_routes", __name__)
dining_db = DiningDatabase()
gym_db = GymDatabase()


@occupancy_routes.route("/v1/occupancy", methods=["GET"])
def get_hours():
    """
    Gets occupancy for all facilities, currently that is only dining halls and gyms.

    Example:
    - `/v1/occupancy` → Returns list of occupants and capacity for each facility that has them
    """
    occupancies = {}

    logger.info("Fetching occupancy for dining halls")
    for slug in OCCUSPACE_IDS:
        hall = dining_db.get_latest_dining_capacity(slug)
        if hall:
            occupancies[slug] = {"occupants": hall.occupants, "capacity": hall.capacity}
        else:
            return jsonify(
                {
                    "error": f"Cannot find occupancy data for dining hall {slug}",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 404

    logger.info("Fetching occupancy for gyms")
    for slug in FACILITY_IDS:
        gym = gym_db.get_latest_gym_capacity(slug)
        if gym:
            occupancies[slug] = {
                zone.zone_name: {"occupants": zone.occupants, "capacity": zone.capacity}
                for zone in gym
            }
        else:
            return jsonify(
                {
                    "error": f"Cannot find occupancy data for gym {slug}",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 404

    return jsonify({"data": occupancies, "timestamp": datetime.now().isoformat()})
