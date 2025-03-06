import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

from config.rec import PROFILE_URL, AUTH_CHECK_URL, RESERVE_URL, BASE_URL

class RecScrapers:
    @staticmethod
    def get_party_id(aspnet_cookie: str) -> Optional[str]:
        """Extracts the user's Party ID from their profile page."""
        url = PROFILE_URL
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}

        try:
            response = requests.get(url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            party_id_field = soup.find("input", {"id": "profileUserId"})
            return party_id_field["value"] if party_id_field else None
        except Exception as e:
            logger.error(f"⚠️ Error fetching Party ID: {e}")
            return None

    @staticmethod
    def is_user_authenticated(aspnet_cookie: str) -> bool:
        """Checks if the user session is still valid."""
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}

        try:
            response = requests.get(AUTH_CHECK_URL, cookies=cookies)
            response.raise_for_status()
            return response.json().get("IsAuthenticated", False)
        except Exception as e:
            logger.error(f"⚠️ Error checking authentication: {e}")
            return False

    @staticmethod
    def fetch_booking_dates(aspnet_cookie: str) -> List[Dict]:
        """Fetches available booking dates."""
        url = f"{BASE_URL}/booking/02a10035-6fd3-48b1-9a1f-648f6368c09a/dates"
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}

        try:
            response = requests.get(url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            date_buttons = soup.find_all("button", class_="single-date-select-button")

            return [
                {
                    "year": btn.get("data-year"),
                    "month": btn.get("data-month"),
                    "day": btn.get("data-day"),
                    "date_text": btn.get("data-date-text"),
                }
                for btn in date_buttons
            ]
        except Exception as e:
            logger.error(f"⚠️ Error fetching booking dates: {e}")
            return []

    @staticmethod
    def get_facility_availability(facility_id: str, aspnet_cookie: str) -> List[Dict]:
        """Fetches available courts and their details for a facility."""
        url = f"{BASE_URL}/booking/{facility_id}/facilities"
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}

        try:
            response = requests.get(url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            courts = []

            for btn in soup.find_all("button", class_="booking-facility-list"):
                courts.append({
                    "court_id": btn.get("id"),
                    "facility_id": btn.get("data-facility-id"),
                    "court_name": btn.get("data-facility-name") or "Unknown Court",
                })

            return courts
        except Exception as e:
            logger.error(f"⚠️ Error fetching facility availability: {e}")
            return []

    @staticmethod
    def get_available_slots(facility_id: str, court_id: str, date: Dict, aspnet_cookie: str) -> List[Dict]:
        """Fetches available time slots for a specific court on a given date."""
        url = f"{BASE_URL}/booking/{facility_id}/slots/{court_id}/{date['year']}/{date['month']}/{date['day']}"
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}

        try:
            response = requests.get(url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            slots = []
            for item in soup.find_all("div", class_="booking-slot-item"):
                button = item.find("button")
                if button:
                    slots.append({
                        "aid": button.get("data-apt-id"),
                        "tsId": button.get("data-timeslot-id"),
                        "tsiId": button.get("data-timeslotinstance-id"),
                        "time": item.find("strong").get_text(strip=True),
                        "availability": "available" if "Booked" not in button.get_text(strip=True) else "booked"
                    })

            return slots
        except Exception as e:
            logger.error(f"⚠️ Error fetching slot availability: {e}")
            return []

    @staticmethod
    def reserve_court(facility_id: str, court_id: str, slot: Dict, aspnet_cookie: str) -> bool:
        """Attempts to reserve a court by sending a POST request."""
        url = RESERVE_URL
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}
        data = {
            "bId": facility_id,
            "fId": court_id,
            "aId": slot["aid"],
            "tsId": slot["tsId"],
            "tsiId": slot["tsiId"],
            "y": slot["year"],
            "m": slot["month"],
            "d": slot["day"],
            "t": "",
            "v": "0",
        }

        try:
            response = requests.post(url, cookies=cookies, data=data)
            return "success" in response.text.lower()
        except Exception as e:
            logger.error(f"⚠️ Error reserving court: {e}")
            return False

    @staticmethod
    def attempt_reservation(facility_id: str, aspnet_cookie: str) -> bool:
        """Full reservation flow: finds an available slot and attempts to book it."""
        if not RecScrapers.is_user_authenticated(aspnet_cookie):
            logger.error("❌ User is not authenticated. Cannot proceed with reservation.")
            return False

        dates = RecScrapers.fetch_booking_dates(aspnet_cookie)
        if not dates:
            logger.error("⚠️ No available dates found.")
            return False

        date = dates[0]  # Pick the first available date
        courts = RecScrapers.get_facility_availability(facility_id, aspnet_cookie)
        if not courts:
            logger.error("⚠️ No available courts found.")
            return False

        court = courts[0]  # Pick the first available court
        slots = RecScrapers.get_available_slots(facility_id, court["court_id"], date, aspnet_cookie)
        if not slots:
            logger.error("⚠️ No available time slots found.")
            return False

        slot = slots[0]  # Pick the first available slot
        return RecScrapers.reserve_court(facility_id, court["court_id"], slot, aspnet_cookie)
