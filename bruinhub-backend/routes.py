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
    Get latest data for a specific gym.
    
    Example:
    - `/v1/gym/bfit` → Returns data for BFIT gym.
    - `/v1/gym/john-wooden-center` → Returns data for Wooden Center.
    """
    data = gym_db.get_gym_latest(slug)
    if not data:
        return jsonify({"error": "Gym not found", "timestamp": datetime.now().isoformat()}), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@api.route("/v1/dining/<slug>", methods=["GET"])
def get_dining_hall(slug: str):
    """
    Retrieves data for a specific dining hall.

    Example:
    - `/v1/dining/epicuria` → Returns data for Epicuria dining hall.
    - `/v1/dining/de-neve` → Returns data for De Neve.
    """
    logger.info(f"Fetching dining hall data for {slug}")

    data = dining_db.get_dining_hall_latest(slug)
    if not data:
        logger.warning(f"Dining hall '{slug}' not found")
        return jsonify({"error": "Dining hall not found"}), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})
