import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
import re
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
    
    # Validate period parameter if provided
    period = request.args.get('period')
    if period and period not in ['day', 'week', 'month', 'year']:
        return jsonify({
            "error": f"Invalid period parameter: {period}. Valid values are: day, week, month, year",
            "timestamp": datetime.now().isoformat()
        }), 400
    
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
    
    # Validate date parameter if provided
    date = request.args.get('date')
    if date:
        # Check if date matches YYYY-MM-DD format and is valid
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date):
            return jsonify({
                "error": f"Invalid date format: {date}. Use YYYY-MM-DD format.",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        try:
            # Validate date further by attempting to parse it
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                "error": f"Invalid date: {date}. Date does not exist or is in wrong format.",
                "timestamp": datetime.now().isoformat()
            }), 400
    
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