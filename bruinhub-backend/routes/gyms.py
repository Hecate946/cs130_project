import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from database.gyms import GymDatabase
from config.gyms import FACILITY_IDS

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
    try:
        data = gym_db.get_gym_latest(slug)
        if not data:
            return (
                jsonify(
                    {"error": "Gym not found", "timestamp": datetime.now().isoformat()}
                ),
                404,
            )

        return jsonify({"data": data, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"Server error in get_gym_data: {e}")
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@gym_routes.route("/v1/gym", methods=["GET"])
def list_all_gyms():
    """
    List all gyms with optional sorting by occupancy.

    Example:
    - `/v1/gym` → Returns a list of all gyms.
    - `/v1/gym?sort=occupancy&order=desc` → Returns gyms sorted by occupancy in descending order.
    """
    try:
        # Get sorting parameters
        sort_by = request.args.get("sort")
        order = request.args.get("order", "asc")

        # Get all gyms
        gyms = {}
        for slug in FACILITY_IDS:
            gym_data = gym_db.get_gym_latest(slug)
            if gym_data:
                gyms[slug] = gym_data

        # For now, we'll skip actual sorting implementation as it's complex
        # In a real implementation, you would sort based on occupancy metrics

        return jsonify({"data": gyms, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"Server error in list_all_gyms: {e}")
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )
