import logging
import requests
from datetime import datetime, timezone
from database.rec import RecDatabase
from scrapers.rec import RecScrapers
from models.rec import TaskStatus
from config.rec import AUTH_CHECK_URL, VERIFY_URL

logger = logging.getLogger(__name__)

# Global database instance
rec_db = None


def setup_rec_tasks():
    """Sets up database connections for recreation tasks."""
    global rec_db
    logger.info("Setting up recreation tasks with database")
    rec_db = RecDatabase()


def check_and_refresh_sessions():
    """Checks user authentication and refreshes session cookies if needed."""
    logger.info("🔄 Running session authentication check...")

    active_users = rec_db.get_active_users()
    for user in active_users:
        try:
            cookies = {".AspNet.ApplicationCookie": user.aspnet_cookie}
            response = requests.get(AUTH_CHECK_URL, cookies=cookies)

            if response.status_code == 200 and response.json().get("IsAuthenticated", False):
                logger.info(f"✅ User with device_id {user.device_id} is authenticated.")
                
                # Check if a new cookie was issued
                new_cookie = response.cookies.get(".AspNet.ApplicationCookie")
                if new_cookie:
                    rec_db.update_session_cookie(user.device_id, new_cookie)

                # Verify session validity
                verify_response = requests.get(VERIFY_URL, cookies=cookies)
                if verify_response.status_code == 200:
                    logger.info(f"🔹 Session for device_id {user.device_id} is valid.")
                else:
                    logger.warning(f"⚠️ Session verification failed for device_id {user.device_id}.")
                    rec_db.mark_session_invalid(user.id)

            else:
                logger.warning(f"❌ User with device_id {user.device_id} is NOT authenticated. Marking session as invalid.")
                rec_db.mark_session_invalid(user.id)

        except requests.RequestException as e:
            logger.error(f"⚠️ Error checking session for device_id {user.device_id}: {e}")


def attempt_reservations():
    """Processes scheduled reservation tasks at their exact scheduled time."""
    logger.info("🎯 Attempting scheduled court reservations...")

    now = datetime.now(timezone.utc)
    pending_tasks = rec_db.get_pending_reservation_tasks()

    for task in pending_tasks:
        if task.schedule_at > now:
            continue  # Skip tasks that are scheduled for the future

        user = rec_db.get_user_by_device_id(task.device_id)
        if not user:
            logger.error(f"⚠️ No user found for reservation task {task.id}. Skipping.")
            continue

        # Extract authentication cookie
        aspnet_cookie = user.aspnet_cookie

        # Ensure user session is valid
        if not RecScrapers.is_user_authenticated(aspnet_cookie):
            logger.error(f"❌ User with device_id {user.device_id} is not authenticated. Skipping task {task.id}.")
            rec_db.mark_session_invalid(user.id)
            continue

        # Step 1: Get available booking dates
        dates = RecScrapers.fetch_booking_dates(aspnet_cookie)
        if not dates:
            logger.warning(f"⚠️ No available booking dates for task {task.id}.")
            continue

        # Ensure we are booking exactly 3 days in advance
        target_date = task.desired_date
        valid_date = next((d for d in dates if d["year"] == str(target_date.year) and
                          d["month"] == str(target_date.month) and d["day"] == str(target_date.day)), None)

        if not valid_date:
            logger.warning(f"⚠️ Desired booking date {target_date} is not available.")
            continue

        # Step 2: Find available courts for the facility
        courts = RecScrapers.get_facility_availability(task.facility_id, aspnet_cookie)
        if not courts:
            logger.warning(f"⚠️ No courts available for facility {task.facility_id}.")
            continue

        # Pick the first available court
        court = courts[0]

        # Step 3: Get available time slots for the court
        slots = RecScrapers.get_available_slots(task.facility_id, court["court_id"], valid_date, aspnet_cookie)
        if not slots:
            logger.warning(f"⚠️ No time slots available for court {court['court_name']}.")
            continue

        # Pick the first available time slot
        slot = slots[0]

        # Step 4: Attempt to reserve the court
        success = RecScrapers.reserve_court(
            facility_id=task.facility_id,
            court_id=court["court_id"],
            slot={
                "aid": slot["aid"],
                "tsId": slot["tsId"],
                "tsiId": slot["tsiId"],
                "year": valid_date["year"],
                "month": valid_date["month"],
                "day": valid_date["day"],
            },
            aspnet_cookie=aspnet_cookie
        )

        # Step 5: Mark reservation as completed if successful, otherwise mark as failed
        if success:
            logger.info(f"✅ Successfully reserved court for task {task.id}.")
            rec_db.mark_reservation_task_completed(task.id)
        else:
            logger.warning(f"⚠️ Failed to reserve court for task {task.id}. Marking as failed.")
            rec_db.mark_reservation_task_failed(task.id)
