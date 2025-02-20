from flask import Blueprint, jsonify
from datetime import datetime
from database.gyms import GymDatabase
from database.dining import DiningDatabase
from database import DatabaseManager
import os

api = Blueprint("api", __name__)

# Initialize database managers
db_manager = DatabaseManager(os.getenv("DATABASE_URL"))
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

