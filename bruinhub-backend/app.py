from flask import Flask
from flask_cors import CORS
import os
from database import DatabaseManager
from routes import api
from database.db import db
import logging
from config.base import DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register the API blueprint
app.register_blueprint(api, url_prefix="/api")

# Load configuration
DB_URL = DATABASE_URL

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize database manager
db_manager = DatabaseManager(DB_URL)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
