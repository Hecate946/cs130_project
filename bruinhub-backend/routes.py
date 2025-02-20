import logging
from flask import Blueprint, jsonify
from datetime import datetime
from database.gyms import GymDatabase
from database.dining import DiningDatabase
from database import DatabaseManager
import os
from config import DATABASE_URL

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)

# Initialize database managers
db_manager = DatabaseManager(DATABASE_URL)
gym_db = GymDatabase(db_manager)
dining_db = DiningDatabase(db_manager)


@api.route("/v1/gym/<slug>", methods=["GET"])
def get_gym_data(slug: str):
    """
    Get latest data for a specific gym

    BFIT slug: 'bfit'
    Wooden slug: 'wooden'
    """
    data = gym_db.get_gym_latest(slug)
    if not data:
        return (
            jsonify(
                {"error": "Gym not found", "timestamp": datetime.now().isoformat()}
            ),
            404,
        )

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@api.route("/v1/dining/halls", methods=["GET"])
def get_dining_halls():
    """
    Retrieves all dining halls and their menu items.
    """
    logger.info("Fetching dining hall data")

    data = dining_db.get_all_dining_halls()

    if not data:
        logger.warning("No dining hall data found")
        return jsonify({"error": "No dining hall data available"}), 404

    return jsonify(data)