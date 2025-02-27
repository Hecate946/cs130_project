from flask import Flask
import os
from database import DatabaseManager
from tasks import init_scheduler
from tasks.gym_tasks import setup_gym_tasks, scrape_and_store_gym_data
from tasks.dining_tasks import setup_dining_tasks, scrape_and_store_dining_data
from tasks.library_tasks import setup_library_tasks, scrape_and_store_library_data
import logging
from config.base import DATABASE_URL
from database.db import db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
DB_URL = DATABASE_URL
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "300"))  # Default 5 minutes

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.app_context().push()
db.create_all()

# Setup tasks
setup_gym_tasks(DB_URL)
setup_dining_tasks(DB_URL)
setup_library_tasks(DB_URL)

if __name__ == "__main__":
    # Initialize scheduler
    scheduler = init_scheduler(app, SCRAPE_INTERVAL)

    # Initial scrape on startup
    scrape_and_store_gym_data()
    scrape_and_store_dining_data()
    scrape_and_store_library_data()

    # Run the app (this will keep the scheduler running)
    app.run(debug=True, host="0.0.0.0", port=5002) 