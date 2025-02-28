import logging
from flask import Blueprint, jsonify
from datetime import datetime
from database.dining import DiningDatabase
from config.dining import OCCUSPACE_IDS

logger = logging.getLogger(__name__)

dining_routes = Blueprint("dining_routes", __name__)
dining_db = DiningDatabase()

@dining_routes.route("/v1/dining", methods=["GET"])
def get_dining_halls():
    """
    Get all dining halls.
    
    Example:
    - `/v1/dining` → Returns list of all dining halls with current status.
    """
    logger.info("Fetching all dining halls data")
    
    all_data = {}
    for slug in OCCUSPACE_IDS:  # Use OCCUSPACE_IDS for all dining locations
        data = dining_db.get_dining_hall_latest(slug)
        if data:
            all_data[slug] = data
    
    return jsonify({
        "data": all_data,
        "timestamp": datetime.now().isoformat()
    })

@dining_routes.route("/v1/dining/<slug>", methods=["GET"])
def get_dining_hall(slug: str):
    """
    Get data for a specific dining hall.
    
    Example:
    - `/v1/dining/epicuria-covel` → Returns data for Epicuria at Covel.
    """
    logger.info(f"Fetching dining hall data for {slug}")
    
    if slug not in OCCUSPACE_IDS:
        return jsonify({
            "error": "Invalid dining hall slug",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    data = dining_db.get_dining_hall_latest(slug)
    if not data:
        return jsonify({
            "error": "Dining hall not found",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "data": data,
        "timestamp": datetime.now().isoformat()
    }) 