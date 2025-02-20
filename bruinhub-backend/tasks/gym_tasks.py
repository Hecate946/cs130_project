import logging
from database import DatabaseManager
from database.gyms import GymDatabase
from scrapers.gyms import GymScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
db_manager = None
gym_db = None
scraper = None


def setup_gym_tasks(database_url: str):
    """Setup database connections and scrapers for gym tasks"""
    global db_manager, gym_db, scraper
    logger.info("Setting up gym tasks with database and scrapers")
    db_manager = DatabaseManager(database_url)
    gym_db = GymDatabase(db_manager)
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
                    logger.info(f"Storing capacity for {slug} - {zone['zone_name']}")
                    gym_db.insert_gym_capacity(
                        slug, zone["zone_name"], zone["last_count"]
                    )

        # Scrape hours
        logger.info("Scraping hours")
        hours_data = scraper.scrape_hours()
        for slug, hours in hours_data.items():
            logger.info(f"Updating hours for {slug}")
            gym_db.update_gym_hours(
                slug,
                hours["regular_hours"],
                hours.get("special_hours"),
            )

    except Exception as e:
        logger.error(f"Error in periodic gym data scraping: {e}", exc_info=True)
