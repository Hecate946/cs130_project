import logging
from database import DatabaseManager
from database.dining import DiningDatabase
from scrapers.dining import DiningScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
# These will be set by the setup function
db_manager = None
dining_db = None
scraper = None


def setup_dining_tasks(database_url: str):
    """Setup database connections and scrapers for dining tasks"""
    global db_manager, dining_db, scraper
    logger.info("Setting up dining tasks with database and scrapers")
    db_manager = DatabaseManager(database_url)
    dining_db = DiningDatabase(db_manager)
    scraper = DiningScrapers()


def scrape_and_store_dining_data():
    """Periodic task to scrape and store dining hall data"""
    try:
        logger.info("Starting periodic dining hall data scraping")

        # Scrape dining data
        logger.info("Scraping dining hall data")
        dining_data = scraper.scrape_dining_halls()

        if dining_data:
            for hall_name, hall_info in dining_data.items():
                logger.info(f"Storing menu snapshot for {hall_name}")
                dining_db.create_menu_snapshot(hall_name, hall_info)

                logger.info(f"Storing hours snapshot for {hall_name}")
                dining_db.update_dining_hours(
                    hall_name, hall_info["hours"], hall_info.get("special_hours", None)
                )

    except Exception as e:
        logger.error(f"Error in periodic dining hall scraping: {e}", exc_info=True)
