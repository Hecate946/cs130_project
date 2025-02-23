import logging
from datetime import datetime
from tasks.dining_tasks import setup_dining_tasks, scrape_and_store_dining_data
from config import DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Test dining tasks"""
    try:
        logger.info("Starting dining tasks test...")
        
        # Setup dining tasks
        logger.info("Setting up dining tasks...")
        setup_dining_tasks(DATABASE_URL)
        
        # Run the scrape and store task
        logger.info("Running scrape and store task...")
        scrape_and_store_dining_data()
        
        logger.info("✅ Dining tasks completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()