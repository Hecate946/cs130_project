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
        
        # Scrape facility counts
        logger.info("Scraping facility counts")
        facility_counts = scraper.scrape_facility_counts()
        for slug, zones in facility_counts.items():
            if zones:  # Only store if we got data
                logger.info(f"Storing {slug} zones snapshot")
                gym_db.create_gym_zones_snapshot(slug, zones)

        # Scrape hours
        logger.info("Scraping hours")
        hours_data = scraper.scrape_hours()
        for slug, hours in hours_data.items():
            logger.info(f"Storing {slug} hours snapshot")
            gym_db.update_gym_hours(
                slug,
                hours['regular_hours'],
                hours.get('special_hours')
            )
            
    except Exception as e:
        logger.error(f"Error in periodic scraping: {e}")
