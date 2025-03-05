import logging
from datetime import datetime

from flask import Blueprint, jsonify
from models.dining import DiningHall
from models.gym import Gym

logger = logging.getLogger(__name__)

hours_route = Blueprint("hours_route", __name__)


@hours_route.route("/v1/hours", methods=["GET"])
def get_hours():
    """
    Gets hours for all facilities, currently that is only dining halls and gyms.

    Example:
    - `/v1/hours` → Returns list of hours for each facility that has them
    """
    logger.info("Fetching hours data for dining halls")
    halls = DiningHall.query.all()

    logger.info("Fetching hours data for gyms")
    gyms = Gym.query.all()

    hours = {slug: hall["hours_today"] for slug, hall in halls.items()} | {
        slug: gym["regular_hours"] for slug, gym in gyms.items()
    }

    return jsonify({"data": hours, "timestamp": datetime.now().isoformat()})
