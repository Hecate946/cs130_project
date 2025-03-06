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


def get_authenticated_user(party_id: str):
    """Fetch user from database and check if they are authenticated."""
    user = rec_db.get_user_by_party_id(party_id)
    if not user:
        return None, "User not found"

    if not RecScrapers.is_user_authenticated(user.aspnet_cookie):
        return None, "User session expired or invalid"

    return user, None


@rec_routes.route("/v1/rec/login", methods=["POST"])
def login():
    """
    Login endpoint.
    Expects a JSON payload with:
      {
          "aspnet_cookie": "<cookie_value>"
      }
    """
    data = request.get_json()
    if not data or "aspnet_cookie" not in data:
        return jsonify({"error": "Missing aspnet_cookie"}), 400

    aspnet_cookie = data["aspnet_cookie"]
    logger.info("Received login request.")

    # Fetch Party ID using RecScrapers
    party_id = RecScrapers.get_party_id(aspnet_cookie)
    if not party_id:
        return jsonify({"error": "Failed to fetch party id, invalid cookie"}), 401

    logger.info(f"Fetched party_id: {party_id}")
    
    # Create or update user
    user = rec_db.create_or_update_user(party_id, aspnet_cookie)
    logger.info(f"User created/updated: {user.party_id}")

    # Create or update session task
    rec_db.create_or_update_session_task(user.id, TaskStatus.running)
    
    return jsonify({
        "userId": user.id,
        "partyId": user.party_id,
        "lastLogin": user.last_login.isoformat()
    }), 200


@rec_routes.route("/v1/rec/profile", methods=["GET"])
def get_profile():
    """
    Profile endpoint.
    Requires `partyId` query parameter.
    Fetches the user's stored authentication cookie and checks session status.
    """
    party_id = request.args.get("partyId")
    
    if not party_id:
        return jsonify({"error": "Missing partyId"}), 400

    logger.info(f"Fetching profile for partyId: {party_id}")

    # Validate user authentication
    user, error = get_authenticated_user(party_id)
    if not user:
        return jsonify({"error": error}), 401

    return jsonify({
        "partyId": party_id,
        "authenticated": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@rec_routes.route("/v1/rec/reserve", methods=["POST"])
def reserve_court():
    """
    Reserve Court endpoint.
    Requires a valid user session.
    Expects a JSON payload with:
      {
          "partyId": "<party_id>",
          "facilityId": "<facility_id>",
          "courtId": "<court_id>",
          "date": { "year": "2025", "month": "3", "day": "10" }
      }
    """
    data = request.get_json()
    required_keys = {"partyId", "facilityId", "courtId", "date"}
    if not data or not required_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    party_id = data["partyId"]
    facility_id = data["FacilityId"]
    court_id = data["courtId"]
    date = data["date"]  # { "year": "2025", "month": "3", "day": "10" }

    logger.info(f"Received reservation request for {party_id} on {date}")

    # Validate user authentication
    user, error = get_authenticated_user(party_id)
    if not user:
        return jsonify({"error": error}), 401

    # Fetch available slots
    slots = RecScrapers.get_available_slots(facility_id, court_id, date, user.aspnet_cookie)
    if not slots:
        return jsonify({"error": "No available slots for this court on the selected date"}), 400

    # Pick the first available slot
    slot = slots[0]

    # Attempt reservation
    success = RecScrapers.reserve_court(
        facility_id=facility_id,
        court_id=court_id,
        slot={
            "aid": slot["aid"],
            "tsId": slot["tsId"],
            "tsiId": slot["tsiId"],
            "year": date["year"],
            "month": date["month"],
            "day": date["day"]
        },
        aspnet_cookie=user.aspnet_cookie
    )

    if success:
        logger.info(f"✅ Successfully reserved court for {party_id}")

        # Store the reservation in the database
        rec_db.store_reservation(
            user_id=user.id,
            facility_id=facility_id,
            court_slot=court_id,
            court_name=f"Facility {facility_id} - Court {court_id}",
            start_time=f"{date['year']}-{date['month']}-{date['day']}T{slot['time']}",
            end_time=f"{date['year']}-{date['month']}-{date['day']}T{slot['time']}",  # Placeholder, real end time should be determined
            participant_id=slot["aid"]
        )

        return jsonify({"success": True, "message": "Reservation successful"}), 200
    else:
        logger.warning(f"⚠️ Failed to reserve court for {party_id}")
        return jsonify({"error": "Reservation failed"}), 500

@rec_routes.route("/v1/rec/reservations", methods=["GET"])
def get_reservations():
    """
    Get all active reservations for a user.
    Requires `partyId` query parameter.
    """
    party_id = request.args.get("partyId")

    if not party_id:
        return jsonify({"error": "Missing partyId"}), 400

    logger.info(f"Fetching reservations for partyId: {party_id}")

    # Validate user authentication
    user, error = get_authenticated_user(party_id)
    if not user:
        return jsonify({"error": error}), 401

    # Fetch reservations from the database
    reservations = rec_db.get_user_reservations(user.id)

    # Format the response
    response = [
        {
            "reservationId": res.id,
            "facilityId": res.facility_id,
            "courtSlot": res.court_slot,
            "courtName": res.court_name,
            "startTime": res.start_time.isoformat(),
            "endTime": res.end_time.isoformat(),
            "canceled": res.canceled
        }
        for res in reservations
    ]

    return jsonify(response), 200

@rec_routes.route("/api/v1/rec/available", methods=["GET"])
def get_available_courts():
    """
    Get all available courts for all facilities on all available dates.
    Requires a valid user session.
    """
    from config.rec import REC_FACILITIES  # Facility IDs from config

    party_id = request.args.get("partyId")
    if not party_id:
        return jsonify({"error": "Missing partyId"}), 400

    logger.info(f"Fetching available courts and slots for partyId: {party_id}")

    # Validate user authentication
    user, error = get_authenticated_user(party_id)
    if not user:
        return jsonify({"error": error}), 401

    available_courts = {}

    # Fetch available dates first using the user's valid cookie
    available_dates = RecScrapers.fetch_booking_dates(user.aspnet_cookie)
    if not available_dates:
        return jsonify({"error": "No available booking dates found"}), 400

    # Loop through all facilities
    for facility in REC_FACILITIES:
        facility_id = facility["id"]
        facility_name = facility["name"]

        facility_availability = {
            "facilityId": facility_id,
            "facilityName": facility_name,
            "availableDates": []
        }

        # Get available courts
        courts = RecScrapers.get_facility_availability(facility_id, user.aspnet_cookie)
        if not courts:
            logger.warning(f"⚠️ No courts available for {facility_name}")
            continue  # Skip facility if no courts are available

        # Limit slot checks to first `N` courts per facility (adjust `N` to avoid overloading API)
        N = 3
        courts = courts[:N]

        print("COURTS", courts)

        # Loop through all available dates
        for date in available_dates:
            date_entry = {
                "date": f"{date['year']}-{date['month']}-{date['day']}",
                "availableCourts": []
            }

            # Loop through each court and get available time slots
            for court in courts:
                try:
                    slots = RecScrapers.get_available_slots(facility_id, court["facility_id"], date, user.aspnet_cookie)
                    print("SALOTS", slots)
                    if not slots:
                        continue  # Skip courts with no slots available

                    date_entry["availableCourts"].append({
                        "courtId": court["court_id"],
                        "courtName": court["court_name"],
                        "availableSlots": len(slots),
                        "slots": [{"time": slot["time"], "aid": slot["aid"], "tsId": slot["tsId"], "tsiId": slot["tsiId"]} for slot in slots]
                    })

                except Exception as e:
                    logger.error(f"⚠️ Error fetching slots for {court['court_name']} on {date_entry['date']}: {e}")
                    continue  # Continue processing other courts even if one fails

            # Add to facility's available dates if there are courts with available slots
            if date_entry["availableCourts"]:
                facility_availability["availableDates"].append(date_entry)

        # Only add facility if it has availability
        if facility_availability["availableDates"]:
            available_courts[facility_id] = facility_availability

    return jsonify(available_courts), 200
