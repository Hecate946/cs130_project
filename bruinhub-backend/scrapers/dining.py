from typing import Dict
import requests
from bs4 import BeautifulSoup
import logging
from config.dining import OCCUSPACE_PREFIX, MENUS_PREFIX, RESTAURANTS, OCCUSPACE_IDS

logger = logging.getLogger(__name__)


class DiningScrapers:
    """Handles scraping of UCLA dining data from various sources"""

    @staticmethod
    def _get_hours_today(slug: str) -> Dict[str, str]:
        """Returns the hours of operation for today."""
        try:
            data = requests.get(f"{OCCUSPACE_PREFIX}/{OCCUSPACE_IDS[slug]}/hours").json()
            hours = next(rules["hours"] for rules in data["data"][0]["rules"] if rules["active"])
            return hours
        except Exception as e:
            logger.error(f"Error fetching hours for {slug}: {str(e)}")
            return {}

    @staticmethod
    def _get_occupancy(slug: str) -> tuple[int, int]:
        """Returns number of people and the capacity of the restaurant."""
        try:
            data = requests.get(f"{OCCUSPACE_PREFIX}/{OCCUSPACE_IDS[slug]}").json()
            return data["data"]["people"], data["data"]["capacity"]
        except Exception as e:
            logger.error(f"Error fetching occupancy for {slug}: {str(e)}")
            return None, None

    @staticmethod
    def _get_menu(slug: str) -> Dict[str, list[str]]:
        """Returns the menu for the restaurant."""
        try:
            response = requests.get(f"{MENUS_PREFIX}/{RESTAURANTS[slug]}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            return {
                str(section.contents[0]).strip(): [elem.text for elem in section.select("a")]
                for section in soup.select("li.sect-item")
            }
        except Exception as e:
            logger.error(f"Error fetching menu for {slug}: {str(e)}")
            return {}

    @staticmethod
    def scrape_dining_halls() -> Dict:
        """
        Scrapes and returns dining hall data including occupancy, menu, and hours.
        
        Returns:
            Dict: A dictionary containing data for all dining locations with structure:
            {
                "slug": {
                    "menu": Dict[str, list[str]],
                    "capacity": int,
                    "occupants": int,
                    "regular_hours": Dict[str, str]
                }
            }
        """
        logger.info("Starting dining hall data scrape")
        dining_data = {}

        for slug in RESTAURANTS:
            try:
                logger.info(f"Scraping data for {slug}")
                occupants, capacity = DiningScrapers._get_occupancy(slug)
                
                dining_data[slug] = {
                    "menu": DiningScrapers._get_menu(slug),
                    "capacity": capacity,
                    "occupants": occupants,
                    "hours_today": DiningScrapers._get_hours_today(slug)
                }
                
                logger.info(f"Successfully scraped data for {slug}")
            except Exception as e:
                logger.error(f"Error scraping data for {slug}: {str(e)}")
                continue

        return dining_data


if __name__ == "__main__":
    import json
    # Configure logging for standalone testing
    logging.basicConfig(level=logging.INFO)
    # Test the scraper
    scraper = DiningScrapers()
    print(json.dumps(scraper.scrape_dining_halls(), indent=4))

