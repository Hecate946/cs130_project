import logging
from database.gyms import GymDatabase
from scrapers.gyms import GymScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
gym_db = None
scraper = None


def setup_gym_tasks():
    """Setup database connections and scrapers for gym tasks"""
    global gym_db, scraper
    logger.info("Setting up gym tasks with database and scrapers")
    gym_db = GymDatabase()
    scraper = GymScrapers()


def scrape_and_store_gym_data():
    """Periodic task to scrape and store gym data"""
    try:
        logger.info("Starting periodic gym data scraping")

        # Scrape facility counts (zone capacities)
        logger.info("Scraping facility counts")
        facility_counts = scraper.scrape_facility_counts()
        for slug, zones in facility_counts.items():
            if zones:  # Only store if we got data
                for zone in zones:
                    logger.info(
                        f"Storing capacity for {slug} - {zone['zone_name']}")
                    gym_db.insert_gym_capacity(
                        slug,
                        zone["zone_name"],
                        zone["last_count"],
                        zone["percentage"],
                        zone[
                            "last_updated"
                        ],  # This will be the LastUpdatedDateAndTime from the API
                    )

    except Exception as e:
        logger.error(
            f"Error in periodic gym data scraping: {e}", exc_info=True)
