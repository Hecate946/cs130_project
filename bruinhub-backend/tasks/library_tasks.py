import logging
from database import DatabaseManager
from database.library import LibraryDatabase
from scrapers.library import LibraryScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
# These will be set by the setup function
db_manager = None
libraries_db = None
scraper = None


def setup_library_tasks(database_url: str):
    """Setup database connections and scrapers for library tasks"""
    global db_manager, libraries_db, scraper
    logger.info("Setting up library tasks with database and scrapers")
    db_manager = DatabaseManager(database_url)
    libraries_db = LibraryDatabase(db_manager)
    scraper = LibraryScrapers()


def scrape_and_store_library_data():
    """Task to scrape library data and store in database"""
    try:
        logger.info("Starting library data scraping")

        # Scrape data
        raw_data = scraper.scrape_library_data()

        # Process each library's data
        for library_id, data in raw_data.items():
            libraries_db.process_library_data(data, library_id, db_manager)

        logger.info("Successfully updated library data")
    except Exception as e:
        logger.error(f"Error in library scraping task: {str(e)}")
