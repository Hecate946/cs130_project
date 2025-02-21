import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from database.gyms import GymDatabase
from database.dining import DiningDatabase
from database.library import LibraryDatabase  # New import for library API
from database import DatabaseManager
import os
from config import DATABASE_URL

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)

# Initialize database managers
db_manager = DatabaseManager(DATABASE_URL)
gym_db = GymDatabase(db_manager)
dining_db = DiningDatabase(db_manager)
library_db = LibraryDatabase(db_manager)


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
        return jsonify(
            {"error": "Gym not found", "timestamp": datetime.now().isoformat()}
        ), 404

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


@api.route("/v1/library/<slug>", methods=["GET"])
def get_library(slug: str):
    """
    Retrieve data for a specific library.

    Example:
    - `/v1/library/powell` → Returns details for Powell Library.
    """
    data = library_db.get_library_details(slug)  # Assumes this method exists.
    if not data:
        return jsonify(
            {"error": "Library not found", "timestamp": datetime.now().isoformat()}
        ), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@api.route("/v1/library/<slug>/bookings", methods=["GET"])
def get_library_bookings(slug: str):
    """
    Retrieve booking data for a specific library.

    Example:
    - `/v1/library/powell/bookings` → Returns current bookings for Powell Library.
    """
    data = library_db.get_library_bookings(slug)  # Assumes this method exists.
    if not data:
        return jsonify(
            {"error": "No booking data found", "timestamp": datetime.now().isoformat()}
        ), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@api.route("/v1/library/<slug>/rooms", methods=["GET"])
def get_library_rooms(slug: str):
    """
    Retrieve rooms for a specific library along with associated booking info.

    Example:
    - `/v1/library/powell/rooms` → Returns rooms and booking details for Powell Library.
    """
    data = library_db.get_library_rooms(slug)
    if not data:
        return jsonify(
            {"error": "No rooms found for this library", "timestamp": datetime.now().isoformat()}
        ), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@api.route("/v1/library/<slug>/bookings/range", methods=["GET"])
def get_library_bookings_by_date_range(slug: str):
    """
    Retrieve booking data for a specific library within a specified date range.

    Query Parameters:
      - start: ISO formatted start datetime (e.g., "2025-02-20T00:00:00")
      - end:   ISO formatted end datetime (e.g., "2025-02-21T00:00:00")

    Example:
      GET /v1/library/powell/bookings/range?start=2025-02-20T00:00:00&end=2025-02-21T00:00:00
    """
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    if not start_str or not end_str:
        return jsonify({
            "error": "Both 'start' and 'end' query parameters are required",
            "timestamp": datetime.now().isoformat()
        }), 400

    try:
        start_date = datetime.fromisoformat(start_str)
        end_date = datetime.fromisoformat(end_str)
    except ValueError as ve:
        logger.error(f"Date parsing error: {ve}")
        return jsonify({
            "error": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)",
            "timestamp": datetime.now().isoformat()
        }), 400

    data = library_db.get_library_bookings_by_date_range(slug, start_date, end_date)
    if not data:
        return jsonify({
            "error": "No booking data found for the specified date range",
            "timestamp": datetime.now().isoformat()
        }), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})
