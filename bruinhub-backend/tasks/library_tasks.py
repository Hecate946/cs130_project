import logging
from database.library import LibraryDatabase
from scrapers.library import LibraryScrapers

logger = logging.getLogger(__name__)

# Initialize global instances
# These will be set by the setup function
library_db = None
scraper = None


def setup_library_tasks():
    """Setup database connections and scrapers for library tasks"""
    global library_db, scraper
    logger.info("Setting up library tasks with database and scrapers")
    library_db = LibraryDatabase()
    scraper = LibraryScrapers()


def scrape_and_store_library_data():
    """Task to scrape library data and store in database"""
    try:
        logger.info("Starting library data scraping")

        # Scrape data
        raw_data = scraper.scrape_library_data()
        logger.info(f"Scraped data for {len(raw_data)} libraries")

        # Process each library's data
        for library_name, data in raw_data.items():
            library_id = library_db.get_library_id_by_name(library_name)
            if not library_id:
                logger.warning(f"Library {library_name} not found in database")
                continue
            
            logger.info(f"Processing data for {library_name}")
            library_db.process_library_data(data, library_id)
            logger.info(f"Successfully processed data for {library_name}")

        logger.info("Successfully updated library data")
    except Exception as e:
        logger.error(f"Error in library scraping task: {str(e)}")
