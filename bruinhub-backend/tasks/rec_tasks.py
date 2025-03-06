import logging
import requests
from datetime import datetime, timezone
from database.rec import RecDatabase
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
                logger.info(f"✅ User {user.party_id} is authenticated.")
                
                # Check if a new cookie was issued
                new_cookie = response.cookies.get(".AspNet.ApplicationCookie")
                if new_cookie:
                    rec_db.update_session_cookie(user.party_id, new_cookie)

                # Verify session validity
                verify_response = requests.get(VERIFY_URL, cookies=cookies)
                if verify_response.status_code == 200:
                    logger.info(f"🔹 Session for {user.party_id} is valid.")
                else:
                    logger.warning(f"⚠️ Session verification failed for {user.party_id}.")
                    rec_db.mark_session_invalid(user.id)

            else:
                logger.warning(f"❌ User {user.party_id} is NOT authenticated. Marking session as invalid.")
                rec_db.mark_session_invalid(user.id)

        except requests.RequestException as e:
            logger.error(f"⚠️ Error checking session for {user.party_id}: {e}")


def attempt_reservations():
    """Processes scheduled reservation tasks and attempts to book courts."""
    logger.info("🎯 Attempting scheduled court reservations...")

    pending_tasks = rec_db.get_pending_reservation_tasks()
    for task in pending_tasks:
        user = rec_db.get_user_by_party_id(task.user_id)
        if not user:
            logger.error(f"⚠️ No user found for reservation task {task.id}. Skipping.")
            continue

        cookies = {".AspNet.ApplicationCookie": user.aspnet_cookie}
        booking_url = "https://secure.recreation.ucla.edu/booking/reserve"
        payload = {
            "bId": task.facility_id,
            "fId": task.court_slot,
            "aId": "",  # This may need to be dynamically fetched before reservation.
            "tsId": "",  # This may need to be dynamically fetched before reservation.
            "tsiId": "",  # This may need to be dynamically fetched before reservation.
            "y": task.desired_date.year,
            "m": task.desired_date.month,
            "d": task.desired_date.day,
            "t": "",
            "v": "0"
        }

        try:
            response = requests.post(booking_url, cookies=cookies, data=payload)
            if response.status_code == 200 and "success" in response.text.lower():
                logger.info(f"✅ Successfully reserved court for task {task.id}.")
                rec_db.mark_reservation_task_completed(task.id)
            else:
                logger.warning(f"⚠️ Failed to reserve court for task {task.id}. Response: {response.text}")

        except requests.RequestException as e:
            logger.error(f"⚠️ Error attempting reservation for task {task.id}: {e}")
