from typing import Dict, List
import logging
import requests
from datetime import datetime, timedelta

from config import (
    ALL_LIBRARY_URLS,
    LIBRARY_GRID_ENDPOINT,
    LIBRARY_URL_CONFIG
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
        for url in ALL_LIBRARY_URLS:
            config = LIBRARY_URL_CONFIG.get(url)
            if config:
                params = config["params"]
                headers = config["headers"]
                payload = config["payload"].copy()
                payload["start"] = start_date
                payload["end"] = end_date
            else:
                logger.warning(
                    f"No configuration found for {url}. Skipping...")
                continue

            try:
                logger.info(f"Fetching data from {url}...")
                response = requests.post(
                    LIBRARY_GRID_ENDPOINT, params=params, headers=headers, data=payload)
                response.raise_for_status()
                results[url] = response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch data from {url}")
                logger.error(e)
            print("-----------------")
            print(results)
            print("-----------------")
        return results
