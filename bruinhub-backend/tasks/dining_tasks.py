import logging
from database import DatabaseManager
from database.dining import DiningDatabase
from scrapers.dining import DiningScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
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
            for hall_slug, hall_info in dining_data.items():
                logger.info(f"Updating dining hall data for {hall_slug}")

                # Update dining hall details (menu & hours)
                dining_db.update_dining_hall(
                    slug=hall_slug,
                    menu=hall_info["menu"],
                    regular_hours=hall_info["regular_hours"],
                    special_hours=hall_info.get("special_hours"),
                )

                # Store historical capacity update
                logger.info(f"Storing capacity update for {hall_slug}")
                dining_db.insert_dining_capacity(hall_slug, hall_info["capacity"])

    except Exception as e:
        logger.error(f"Error in periodic dining hall scraping: {e}", exc_info=True)
