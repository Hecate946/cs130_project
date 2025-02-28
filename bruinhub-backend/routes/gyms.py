import logging
from flask import Blueprint, jsonify
from datetime import datetime
from database.gyms import GymDatabase

logger = logging.getLogger(__name__)

gym_routes = Blueprint("gym_routes", __name__)
gym_db = GymDatabase()

@gym_routes.route("/v1/gym/<slug>", methods=["GET"])
def get_gym_data(slug: str):
    """
    Get latest data for a specific gym.

    Example:
    - `/v1/gym/bfit` → Returns data for BFIT gym.
    - `/v1/gym/john-wooden-center` → Returns data for Wooden Center.
    """
    data = gym_db.get_gym_latest(slug)
    if not data:
        return jsonify(
            {"error": "Gym not found", "timestamp": datetime.now().isoformat()}
        ), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()}) 