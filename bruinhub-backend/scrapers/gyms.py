from datetime import datetime
from typing import Dict, List
import logging
import requests
from config import FACILITY_COUNT_URL, BFIT_URL, JWC_URL, FACILITY_IDS

logger = logging.getLogger(__name__)

class GymScrapers:
    @staticmethod
    def get_facility_counts() -> Dict:
        """Get raw facility count data from UCLA's API"""
        try:
            response = requests.get(FACILITY_COUNT_URL)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching facility counts: {e}")
            return {}

    @staticmethod
    def filter_facility_zones(data: List[Dict], facility_id: int) -> List[Dict]:
        """Filter zones for a specific facility and format them"""
        try:
            zones = []
            for zone in data:
                if zone.get("FacilityId") == facility_id:
                    # Calculate percentage ourselves
                    last_count = zone["LastCount"]
                    total_capacity = zone["TotalCapacity"]
                    percentage = round((last_count / total_capacity) * 100) if total_capacity > 0 else 0
                    
                    zones.append({
                        "zone_name": zone["LocationName"],
                        "open": not zone["IsClosed"],
                        "last_count": last_count,
                        "percentage": percentage
                    })
            return zones
        except Exception as e:
            logger.error(f"Error filtering facility zones: {e}")
            return []

    @staticmethod
    def scrape_facility_counts() -> Dict[str, List[Dict]]:
        """Scrapes facility counts for all gyms"""
        logger.info("Starting facility counts scrape")
        try:
            # Get facility counts
            facility_data = GymScrapers.get_facility_counts()
            if not facility_data:
                logger.error("Failed to get facility data")
                return {}

            # Get counts for each facility
            results = {}
            for slug, facility_id in FACILITY_IDS.items():
                zones = GymScrapers.filter_facility_zones(facility_data, facility_id)
                logger.info(f"Found {len(zones)} zones for {slug}")
                results[slug] = zones

            return results

        except Exception as e:
            logger.error(f"Error in facility counts scraping: {e}")
            return {}

    @staticmethod
    def get_static_hours() -> Dict[str, Dict]:
        """Get static hours data (until we implement webpage scraping)"""
        return {
            'bfit': {
                "regular_hours": {
                    "Monday": "6:00 AM - 1:00 AM",
                    "Tuesday": "6:00 AM - 1:00 AM",
                    "Wednesday": "6:00 AM - 1:00 AM",
                    "Thursday": "6:00 AM - 1:00 AM",
                    "Friday": "6:00 AM - 9:00 PM",
                    "Saturday": "9:00 AM - 6:00 PM",
                    "Sunday": "9:00 AM - 11:00 PM"
                },
                "special_hours": {
                    "2025-01-26": "1:00 PM - 11:00 PM",  # Staff meeting
                    "2025-02-15": "9:00 AM - 6:00 PM",   # Presidents Day Weekend
                    "2025-02-16": "9:00 AM - 6:00 PM",
                    "2025-02-17": "9:00 AM - 6:00 PM"
                }
            },
            'john-wooden-center': {
                "regular_hours": {
                    "Monday": "6:00 AM - 11:00 PM",
                    "Tuesday": "6:00 AM - 11:00 PM",
                    "Wednesday": "6:00 AM - 11:00 PM",
                    "Thursday": "6:00 AM - 11:00 PM",
                    "Friday": "6:00 AM - 10:00 PM",
                    "Saturday": "8:00 AM - 8:00 PM",
                    "Sunday": "8:00 AM - 10:00 PM"
                },
                "special_hours": {
                    "2025-01-26": "8:00 AM - 6:00 PM"  # Example special hours
                }
            }
        }

    @staticmethod
    def scrape_hours() -> Dict[str, Dict]:
        """Scrapes hours for all gyms (currently returns static data)"""
        logger.info("Starting hours scrape")
        try:
            # TODO: Implement actual web scraping for hours
            # For now, return static data
            return GymScrapers.get_static_hours()

        except Exception as e:
            logger.error(f"Error in hours scraping: {e}")
            return {} 