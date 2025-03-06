import logging
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from database.rec import RecDatabase
from models.rec import TaskStatus
from scrapers.rec import RecScrapers  # Updated import
from config.rec import REC_FACILITIES

logger = logging.getLogger(__name__)
rec_routes = Blueprint("rec_routes", __name__)
rec_db = RecDatabase()


@rec_routes.route("/v1/rec/login", methods=["POST"])
def login():
    """
    Login endpoint.
    Expects a JSON payload with:
    {
        "device_id": "<device_id>",
        "aspnet_cookie": "<cookie_value>"
    }
    """
    data = request.get_json()
    
    # Validate request payload
    if not data or "device_id" not in data or "aspnet_cookie" not in data:
        return jsonify({"error": "Missing device_id or aspnet_cookie"}), 400

    device_id = data["device_id"]
    aspnet_cookie = data["aspnet_cookie"]
    
    logger.info(f"Received login request from device: {device_id}")

    # Authenticate the user using RecScrapers
    authenticated = RecScrapers.is_user_authenticated(aspnet_cookie)
    if not authenticated:
        return jsonify({"error": "Invalid cookie"}), 401

    # Create or update user in the database
    user = rec_db.create_or_update_user(device_id, aspnet_cookie)
    logger.info(f"User created/updated: {user.device_id}")

    # Create or update session task
    rec_db.create_or_update_session_task(user.id, TaskStatus.running)

    return jsonify({
        "success": True,
    }), 200

@rec_routes.route("/v1/rec/logout", methods=["POST"])
def logout():
    """
    Logout endpoint.
    Cancels the session task and clears the user's authentication cookie.
    Expects a JSON payload with:
    {
        "device_id": "<device_id>"
    }
    """
    data = request.get_json()
    if not data or "device_id" not in data:
        return jsonify({"error": "Missing device_id"}), 400

    device_id = data["device_id"]
    user = rec_db.get_user_by_device_id(device_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Cancel the session task and clear the user's session
    rec_db.cancel_session_task(user.id)
    rec_db.clear_user_session(user.id)

    logger.info(f"✅ User with device_id {device_id} has been logged out.")
    return jsonify({"success": True, "message": "User logged out successfully"}), 200


@rec_routes.route("/v1/rec/check-auth", methods=["GET"])
def check_authentication():
    """
    Authentication check endpoint.
    Requires a 'deviceId' query parameter.
    Checks the user's stored ASP.NET cookie and verifies it with RecScrapers.is_user_authenticated.
    
    Returns:
      - {"authenticated": true} if the cookie is valid.
      - {"authenticated": false} if the user is not found or the cookie is invalid/expired.
    """
    device_id = request.args.get("deviceId")
    
    if not device_id:
        return jsonify({"error": "Missing deviceId"}), 400

    logger.info(f"Checking authentication status for deviceId: {device_id}")
    
    # Fetch the user from the database
    user = rec_db.get_user_by_device_id(device_id)
    if not user:
        logger.info(f"User with deviceId {device_id} not found.")
        return jsonify({"authenticated": False}), 200

    # Check if the user has an ASP.NET cookie stored
    if not user.aspnet_cookie:
        logger.info(f"User with deviceId {device_id} does not have a stored session cookie.")
        return jsonify({"authenticated": False}), 200

    # Re-check the cookie's validity using RecScrapers.is_user_authenticated
    if not RecScrapers.is_user_authenticated(user.aspnet_cookie):
        logger.info(f"Cookie for deviceId {device_id} is invalid or expired.")
        return jsonify({"authenticated": False}), 200

    logger.info(f"User with deviceId {device_id} is authenticated.")
    return jsonify({"authenticated": True}), 200

@rec_routes.route("/v1/rec/available-courts", methods=["GET"])
def get_available_courts_for_facility():
    """
    Returns all available courts for a given facility on a specific date.
    Expects query parameters:
      - deviceId: string
      - facilityId: string
      - year: string (e.g., "2025")
      - month: string (e.g., "3")
      - day: string (e.g., "10")
    
    Verifies that the user is authenticated by directly calling RecScrapers.is_user_authenticated
    with the stored ASP.NET cookie.
    
    Returns a JSON object of the following format:
      {
         "facilityId": "<facilityId>",
         "availableCourts": [
             {
                "courtId": "<court_id>",   # For tennis, a unique id; for pickleball, the facility id.
                "courtName": "<court_name>",
                "availableSlots": <number>,  # Total available slots for this court
                "slots": [
                    {
                        "time": "<slot_time>",
                        "aid": "<appointment id>",
                        "tsId": "<timeslot id>",
                        "tsiId": "<timeslot instance id>"
                    },
                    ...
                ]
             },
             ...
         ]
      }
    """
    device_id = request.args.get("deviceId")
    facility_id = request.args.get("facilityId")
    year = request.args.get("year")
    month = request.args.get("month")
    day = request.args.get("day")
    
    if not device_id or not facility_id or not year or not month or not day:
        return jsonify({"error": "Missing required parameters"}), 400

    logger.info(f"Fetching available courts for facility {facility_id} on {year}-{month}-{day} for deviceId: {device_id}")

    # Retrieve the user from the database
    user = rec_db.get_user_by_device_id(device_id)
    if not user or not user.aspnet_cookie:
        logger.info(f"User with deviceId {device_id} not found or missing session cookie.")
        return jsonify({"error": "User not authenticated"}), 401

    # Use RecScrapers.is_user_authenticated to verify the stored cookie
    if not RecScrapers.is_user_authenticated(user.aspnet_cookie):
        logger.info(f"Cookie for deviceId {device_id} is invalid or expired.")
        return jsonify({"error": "User session expired or invalid"}), 401

    # Build a date dictionary to pass to the scraper
    date = {"year": year, "month": month, "day": day}

    # Retrieve available courts for the facility using the user's cookie
    courts = RecScrapers.get_facility_availability(facility_id, user.aspnet_cookie)
    logger.info(f"Scraper returned courts: {courts}")
    if not courts:
        return jsonify({"error": "No courts available for the specified facility"}), 400

    available_courts = []
    for court in courts:
        try:
            # Use "court_id" if available, otherwise fallback to court["facility_id"]
            court_id = court["facility_id"]
            # For tennis, the scraper returns multiple distinct courts.
            # For pickleball (facility id "02a10035-6fd3-48b1-9a1f-648f6368c09a"), only one court is returned.
            slots = RecScrapers.get_available_slots(facility_id, court_id, date, user.aspnet_cookie)
            print(f"Slots for court {court_id}: {slots}")
            if slots:
                available_courts.append({
                    "courtId": court_id,
                    "courtName": court["court_name"],
                    "availableSlots": len(slots),
                    "slots": [
                        {
                            "time": slot["time"],
                            "aid": slot["aid"],
                            "tsId": slot["tsId"],
                            "tsiId": slot["tsiId"]
                        } for slot in slots
                    ]
                })
        except Exception as e:
            logger.error(f"Error fetching slots for court {court.get('court_name', 'unknown')} on {year}-{month}-{day}: {e}")
            continue

    return jsonify({
        "facilityId": facility_id,
        "availableCourts": available_courts
    }), 200
