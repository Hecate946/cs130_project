from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from database import DatabaseManager
from database.gyms import GymDatabase
from tasks import init_scheduler
from tasks.gym_tasks import setup_gym_tasks, scrape_and_store_gym_data
from tasks.dining_tasks import setup_dining_tasks, scrape_and_store_dining_data
from tasks.library_tasks import setup_library_tasks, scrape_and_store_library_data
from routes import api  # Add this import
from models.library import db
import logging

from config import DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register the API blueprint
app.register_blueprint(api, url_prefix="/api")  # Add this line

# Load configuration
DB_URL = DATABASE_URL
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "15"))  # Default 5 minutes

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize database managers
db_manager = DatabaseManager(DB_URL)

# Setup tasks
setup_gym_tasks(DB_URL)
setup_dining_tasks(DB_URL)
setup_library_tasks(DB_URL)


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    if db_manager.test_connection():
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
        })
    return jsonify({
        "status": "unhealthy",
        "database": "disconnected",
        "timestamp": datetime.now().isoformat(),
    }), 500



if __name__ == "__main__":
    # Initialize scheduler
    scheduler = init_scheduler(app, SCRAPE_INTERVAL)

    # Initial scrape on startup
    scrape_and_store_gym_data()
    scrape_and_store_dining_data()
    scrape_and_store_library_data()

    app.run(debug=True, host="0.0.0.0", port=5001)
