import logging
from datetime import datetime

from config import FACILITY_IDS, OCCUSPACE_IDS
from database.dining import DiningDatabase
from database.gyms import GymDatabase
from flask import Blueprint, jsonify
from models.dining import DiningHall
from models.gyms import Gym

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
    halls = DiningHall.query.all()
    for slug in OCCUSPACE_IDS:
        hall = dining_db.get_latest_dining_capacity(slug)
        if hall:
            data[slug] = {
                "hours": halls[slug]["hours_today"],
                "occupants": hall.occupants,
                "capacity": hall.capacity,
            }
        else:
            return jsonify(
                {
                    "error": f"Cannot find hours and occupancy data for dining hall {slug}",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 404

    logger.info("Fetching hours and occupancy for gyms")
    gyms = Gym.query.all()
    for slug in FACILITY_IDS:
        gym = gym_db.get_latest_gym_capacity(slug)
        if gym:
            data[slug] = {"hours": gyms[slug]["regular_hours"]}
            data[slug].update(
                {
                    zone.zone_name: {
                        "occupants": zone.occupants,
                        "capacity": zone.capacity,
                    }
                    for zone in gym
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
