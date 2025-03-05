import logging
from flask import Blueprint, jsonify
from datetime import datetime
from database.dining import DiningDatabase
from database.gyms import GymDatabase
from config.dining import OCCUSPACE_IDS
from config.gyms import FACILITY_IDS

logger = logging.getLogger(__name__)

historical_routes = Blueprint("historical_routes", __name__)
dining_db = DiningDatabase()
gym_db = GymDatabase()

@historical_routes.route("/v1/historical/dining/<slug>", methods=["GET"])
def get_dining_historical(slug: str):
    """
    Get historical capacity data for a dining hall.
    
    Example:
    - `/v1/historical/dining/bplate` → Returns hourly averages for BruinPlate.
    """
    logger.info(f"Fetching historical data for dining hall: {slug}")
    
    if slug not in OCCUSPACE_IDS:
        return jsonify({
            "error": "Invalid dining hall slug",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    data = dining_db.get_historical_capacity(slug)
    if not data:
        return jsonify({
            "error": "No historical data available",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "data": data,
        "timestamp": datetime.now().isoformat()
    })

@historical_routes.route("/v1/historical/gym/<slug>", methods=["GET"])
def get_gym_historical(slug: str):
    """
    Get historical capacity data for a gym.
    
    Example:
    - `/v1/historical/gym/bfit` → Returns hourly averages for each zone in BFIT.
    """
    logger.info(f"Fetching historical data for gym: {slug}")
    
    if slug not in FACILITY_IDS:
        return jsonify({
            "error": "Invalid gym slug",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    data = gym_db.get_historical_capacity(slug)
    if not data:
        return jsonify({
            "error": "No historical data available",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "data": data,
        "timestamp": datetime.now().isoformat()
    }) 