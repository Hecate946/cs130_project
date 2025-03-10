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
        return (
            jsonify(
                {
                    "error": "No booking data found",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            404,
        )

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
        return (
            jsonify(
                {
                    "error": "No rooms found for this library",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            404,
        )

    return jsonify({"data": data, "timestamp": datetime.now().isoformat()})


@library_routes.route("/v1/library/<slug>/bookings/range", methods=["GET"])
def get_library_bookings_by_date_range(slug):
    """
    Retrieve booking data for a specific library within a specified date range.

    Path Parameters:
    - slug (str): The library identifier (e.g., 'powell', 'yrl')

    Query Parameters:
    - start (str, required): ISO 8601 formatted datetime string for the start of the range
      Format: YYYY-MM-DDThh:mm:ss (e.g., '2025-03-08T00:00:00')
    - end (str, required): ISO 8601 formatted datetime string for the end of the range
      Format: YYYY-MM-DDThh:mm:ss (e.g., '2025-03-08T23:59:59')

    Returns:
    - 200 OK: JSON object with an array of booking objects and a timestamp
      - data: Array of booking objects, possibly empty if no bookings found
      - timestamp: ISO 8601 timestamp of when the response was generated
    - 400 Bad Request: If start/end parameters are missing or in invalid format

    Each booking object contains:
    - id: Unique identifier for the booking
    - room_id: ID of the room being booked
    - start_time: ISO 8601 start time of the booking
    - end_time: ISO 8601 end time of the booking
    - status: Booking status ('available' or 'booked')
    - created_at: ISO 8601 timestamp of when the booking was created

    Examples:

    1. Get all bookings for Powell Library on March 8, 2025:
       GET /v1/library/powell/bookings/range?start=2025-03-08T00:00:00&end=2025-03-08T23:59:59

    2. Get bookings for YRL in the morning hours:
       GET /v1/library/yrl/bookings/range?start=2025-03-10T08:00:00&end=2025-03-10T12:00:00

    3. Get bookings for a specific week:
       GET /v1/library/powell/bookings/range?start=2025-03-01T00:00:00&end=2025-03-07T23:59:59

    Note: This endpoint always returns a 200 status code with an array (possibly empty)
    when parameters are valid, even if no bookings are found in the specified range.
    """
    start = request.args.get("start")
    end = request.args.get("end")

    if not start or not end:
        return (
            jsonify(
                {
                    "error": "Missing start or end date parameters",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            400,
        )

    try:
        # Validate date format
        start_datetime = datetime.fromisoformat(start)
        end_datetime = datetime.fromisoformat(end)
    except ValueError:
        return (
            jsonify(
                {
                    "error": "Invalid date format",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            400,
        )

    data = library_db.get_library_bookings_by_date_range(
        slug, start_datetime, end_datetime
    )

    # Always return 200 with data array (even if empty)
    return jsonify({"data": data or [], "timestamp": datetime.now().isoformat()})


@library_routes.route("/v1/library/<slug>", methods=["GET", "POST"])
def get_library_details(slug: str):
    """
    Get details for a specific library.

    Example:
    - `/v1/library/powell` → Returns Powell Library details.
    """
    if request.method != "GET":
        return (
            jsonify(
                {"error": "Method not allowed", "timestamp": datetime.now().isoformat()}
            ),
            405,
        )

    logger.info(f"Fetching library details for {slug}")

    details = library_db.get_library_details(slug)
    if not details:
        return (
            jsonify(
                {"error": "Library not found", "timestamp": datetime.now().isoformat()}
            ),
            404,
        )

    return jsonify({"data": details, "timestamp": datetime.now().isoformat()})


@library_routes.route("/v1/library", methods=["GET"])
def get_all_libraries():
    """
    Retrieve all libraries.

    Example:
    - `/v1/library` → Returns list of all libraries.
    """
    libraries = library_db.get_all_libraries()
    if not libraries:
        return (
            jsonify(
                {"error": "No libraries found", "timestamp": datetime.now().isoformat()}
            ),
            404,
        )

    return jsonify({"data": libraries, "timestamp": datetime.now().isoformat()})


@library_routes.route("/v1/library/rooms", methods=["GET"])
def get_all_library_rooms():
    """
    Retrieve all library rooms along with their associated IDs.

    Example:
    - `/v1/library/rooms` → Returns list of all library rooms.
    """
    rooms = library_db.get_all_library_rooms()
    if not rooms:
        return (
            jsonify(
                {
                    "error": "No library rooms found",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            404,
        )

    return jsonify({"data": rooms, "timestamp": datetime.now().isoformat()})
