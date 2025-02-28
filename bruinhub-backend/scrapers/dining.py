from typing import Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import logging
from config.dining import (
    OCCUSPACE_PREFIX,
    MENUS_PREFIX,
    OCCUSPACE_IDS,
    MENU_ENABLED_RESTAURANTS,
    supports_menu_scraping,
    get_menu_info
)

logger = logging.getLogger(__name__)


class DiningScrapers:
    """Handles scraping of UCLA dining data from various sources"""

    @staticmethod
    def _get_hours_today(slug: str) -> Dict[str, str]:
        """Returns the hours of operation for today."""
        try:
            occuspace_id = OCCUSPACE_IDS[slug]
            data = requests.get(f"{OCCUSPACE_PREFIX}/{occuspace_id}/hours").json()
            hours = next(rules["hours"] for rules in data["data"][0]["rules"] if rules["active"])
            return hours
        except Exception as e:
            logger.error(f"Error fetching hours for {slug}: {str(e)}")
            return {}

    @staticmethod
    def _get_occupancy(slug: str) -> Tuple[Optional[int], Optional[int]]:
        """Returns number of people and the capacity of the restaurant."""
        try:
            occuspace_id = OCCUSPACE_IDS[slug]
            data = requests.get(f"{OCCUSPACE_PREFIX}/{occuspace_id}").json()
            return data["data"]["people"], data["data"]["capacity"]
        except Exception as e:
            logger.error(f"Error fetching occupancy for {slug}: {str(e)}")
            return None, None

    @staticmethod
    def _get_standard_menu(menu_name: str) -> Dict[str, list[str]]:
        """Returns the menu for restaurants using standard menu format."""
        try:
            response = requests.get(f"{MENUS_PREFIX}/{menu_name}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            return {
                str(section.contents[0]).strip(): [elem.text for elem in section.select("a")]
                for section in soup.select("li.sect-item")
            }
        except Exception as e:
            logger.error(f"Error fetching menu for {menu_name}: {str(e)}")
            return {}
        
    @staticmethod
    def _get_feast_menu(menu_name: str) -> Dict[str, dict]:
        """Returns the menu for restaurants using feast menu format,
        including a section image (if available) that is not a webcode image."""
        try:
            response = requests.get(f"{MENUS_PREFIX}/{menu_name}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            
            main_content = soup.find(id="main-content")
            if not main_content:
                logger.error("Could not locate main-content container.")
                return {}

            sections = {}
            current_section = None
            
            # Helper function to decide if an image tag is valid for a section.
            def is_valid_section_image(img_tag):
                if not img_tag:
                    return False
                src = img_tag.get("src", "")
                # Ignore images that are clearly webcode icons.
                if "/Content/Images/WebCodes/" in src:
                    return False
                # Also check if the class attribute suggests it is a webcode.
                classes = img_tag.get("class", [])
                if any("webcode" in cls for cls in classes):
                    return False
                return True

            for element in main_content.descendants:
                # When we hit a header, start a new section.
                if element.name in ["h2", "h3"]:
                    header_text = element.get_text(strip=True)
                    if header_text:
                        current_section = header_text
                        
                        # Look for a valid image immediately following the header.
                        section_image = None
                        next_elem = element.find_next_sibling()
                        while next_elem:
                            if next_elem.name == "img" and is_valid_section_image(next_elem):
                                src = next_elem.get("src")
                                # Convert relative URL to absolute URL
                                if src and src.startswith("/"):
                                    section_image = f"https://menu.dining.ucla.edu{src}"
                                else:
                                    section_image = src
                                break
                            next_elem = next_elem.find_next_sibling()
                        
                        sections[current_section] = {"image": section_image, "items": []}
                
                # Extract menu items as before.
                if (
                    element.name == "div"
                    and element.get("class")
                    and "menu-item" in element.get("class")
                ):
                    link = element.select_one(".menu-item-name a")
                    if link and current_section:
                        item_text = link.get_text(strip=True)
                        sections[current_section]["items"].append(item_text)
            
            return sections
        except Exception as e:
            logger.error(f"Error fetching menu for {menu_name}: {str(e)}")
            return {}

    def _get_menu(self, slug: str) -> Dict[str, list[str]]:
        """Returns the menu for any restaurant based on its scraper type."""
        if not supports_menu_scraping(slug):
            return {}

        menu_info = get_menu_info(slug)
        scraper_type = menu_info["scraper_type"]
        menu_name = menu_info["menu_name"]

        if scraper_type == "standard":
            return self._get_standard_menu(menu_name)
        elif scraper_type == "feast":
            return self._get_feast_menu(menu_name)
        else:
            logger.error(f"Unknown scraper type: {scraper_type}")
            return {}

    def scrape_dining_halls(self) -> Dict:
        """
        Scrapes and returns dining hall data including occupancy, menu, and hours.
        
        Returns:
            Dict: A dictionary containing data for all dining locations with structure:
            {
                "slug": {
                    "menu": Dict[str, list[str]],
                    "capacity": int,
                    "occupants": int,
                    "hours_today": Dict[str, str]
                }
            }
        """
        logger.info("Starting dining hall data scrape")
        dining_data = {}

        for slug in OCCUSPACE_IDS:
            try:
                logger.info(f"Scraping data for {slug}")
                occupants, capacity = self._get_occupancy(slug)
                
                dining_data[slug] = {
                    "menu": self._get_menu(slug),
                    "capacity": capacity,
                    "occupants": occupants,
                    "hours_today": self._get_hours_today(slug)
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

