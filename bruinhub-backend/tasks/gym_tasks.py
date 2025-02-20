import logging
from database import DatabaseManager
from database.gyms import GymDatabase
from scrapers.gyms import GymScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
# These will be set by the setup function
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

        # Scrape BFIT
        logger.info("Scraping BFIT data")
        bfit_data = scraper.scrape_bfit()
        if bfit_data:
            logger.info("Storing BFIT zones snapshot")
            gym_db.create_gym_zones_snapshot("bfit", bfit_data["zones"])
            logger.info("Storing BFIT hours snapshot")
            gym_db.update_gym_hours(
                "bfit",
                bfit_data["hours"]["regular_hours"],
                bfit_data["hours"]["special_hours"],
            )

        # Scrape Wooden
        logger.info("Scraping Wooden Center data")
        wooden_data = scraper.scrape_wooden()
        if wooden_data:
            logger.info("Storing Wooden zones snapshot")
            gym_db.create_gym_zones_snapshot("john-wooden-center", wooden_data["zones"])
            logger.info("Storing Wooden hours snapshot")
            gym_db.update_gym_hours(
                "john-wooden-center",
                wooden_data["hours"]["regular_hours"],
                wooden_data["hours"]["special_hours"],
            )

    except Exception as e:
        logger.error(f"Error in periodic scraping: {e}")
