import logging
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from config.rec import AUTH_CHECK_URL, VERIFY_URL

logger = logging.getLogger(__name__)


class RecScrapers:
    @staticmethod
    def get_facility_availability(facility_id: str, aspnet_cookie: str) -> Optional[str]:
        """Fetches the availability HTML for a given facility booking page."""
        url = f"https://secure.recreation.ucla.edu/booking/{facility_id}/facilities"
        cookies = {".AspNet.ApplicationCookie": aspnet_cookie}

        try:
            response = requests.get(url, cookies=cookies)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"⚠️ Error fetching availability for {facility_id}: {e}")
            return None

    @staticmethod
    def parse_availability(html: str) -> List[Dict]:
        """Parses the booking page HTML and extracts available courts and their details."""
        soup = BeautifulSoup(html, 'html.parser')

        courts = []
        court_buttons = soup.find_all('button', class_='booking-facility-list')

        for btn in court_buttons:
            court_id = btn.get('id')
            facility_id = btn.get('data-facility-id')
            court_name = btn.get('data-facility-name')

            if not court_name:
                span = btn.find('span')
                court_name = span.get_text(strip=True) if span else "Unknown Court"

            courts.append({
                "court_id": court_id,
                "facility_id": facility_id,
                "court_name": court_name
            })

        return courts

    @staticmethod
    def fetch_and_parse_availability(facility_id: str, aspnet_cookie: str) -> List[Dict]:
        """Fetches and parses the facility availability in one function call."""
        html = RecScrapers.get_facility_availability(facility_id, aspnet_cookie)
        if html:
            return RecScrapers.parse_availability(html)
        return []
