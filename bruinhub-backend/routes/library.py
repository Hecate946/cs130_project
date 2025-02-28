import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from database.library import LibraryDatabase

logger = logging.getLogger(__name__)

library_routes = Blueprint("library_routes", __name__)
library_db = LibraryDatabase()

@library_routes.route("/v1/library/<slug>/bookings", methods=["GET"])
def get_library_bookings(slug: str):
    """
    Retrieve booking data for a specific library.

    Example:
    - `/v1/library/powell/bookings` → Returns current bookings for Powell Library.
    """
    data = library_db.get_library_bookings(slug)
    if not data:
        return jsonify(
            {"error": "No booking data found", "timestamp": datetime.now().isoformat()}
        ), 404

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})

@library_routes.route("/v1/library/<slug>/rooms", methods=["GET"])
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

@library_routes.route("/v1/library/<slug>/bookings/range", methods=["GET"])
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

@library_routes.route("/v1/library/<slug>", methods=["GET", "POST"])
def get_library_details(slug: str):
    """
    Get details for a specific library.
    
    Example:
    - `/v1/library/powell` → Returns Powell Library details.
    """
    if request.method != "GET":
        return jsonify({
            "error": "Method not allowed",
            "timestamp": datetime.now().isoformat()
        }), 405
        
    logger.info(f"Fetching library details for {slug}")
    
    details = library_db.get_library_details(slug)
    if not details:
        return jsonify({
            "error": "Library not found",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    return jsonify({
        "data": details,
        "timestamp": datetime.now().isoformat()
    })

@library_routes.route("/v1/library", methods=["GET"])
def get_all_libraries():
    """
    Retrieve all libraries.
    
    Example:
    - `/v1/library` → Returns list of all libraries.
    """
    libraries = library_db.get_all_libraries()
    if not libraries:
        return jsonify({
            "error": "No libraries found",
            "timestamp": datetime.now().isoformat()
        }), 404

    return jsonify({
        "data": libraries,
        "timestamp": datetime.now().isoformat()
    })

@library_routes.route("/v1/library/rooms", methods=["GET"])
def get_all_library_rooms():
    """
    Retrieve all library rooms along with their associated IDs.
    
    Example:
    - `/v1/library/rooms` → Returns list of all library rooms.
    """
    rooms = library_db.get_all_library_rooms()
    if not rooms:
        return jsonify({
            "error": "No library rooms found",
            "timestamp": datetime.now().isoformat()
        }), 404

    return jsonify({
        "data": rooms,
        "timestamp": datetime.now().isoformat()
    }) 