from typing import Dict, List
import logging
import requests
from datetime import datetime, timedelta

from config.library import (
    LIBRARY_GRID_ENDPOINT,
    LIBRARY_URL_CONFIG,
    ALL_LIBRARY_NAMES
)

logger = logging.getLogger(__name__)


def get_date_range(days=7):
    """Get today's date and X days from now in YYYY-MM-DD format"""
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    future_date = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    return today, future_date


class LibraryScrapers:

    @staticmethod
    def scrape_library_data():
        start_date, end_date = get_date_range()
        results = {}
        for library_name in ALL_LIBRARY_NAMES:
            config = LIBRARY_URL_CONFIG.get(library_name)
            if config:
                params = config["params"]
                headers = config["headers"]
                payload = config["payload"].copy()
                payload["start"] = start_date
                payload["end"] = end_date
            else:
                logger.warning(
                    f"No configuration found for {library_name}. Skipping...")
                continue

            try:
                logger.info(f"Fetching data for {library_name}...")
                response = requests.post(
                    LIBRARY_GRID_ENDPOINT, params=params, headers=headers, data=payload)
                response.raise_for_status()
                results[library_name] = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch data for {library_name}")
                logger.error(e)
        return results

# print(LibraryScrapers.scrape_library_data())