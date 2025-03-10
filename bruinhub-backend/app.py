from flask import Flask, jsonify
from sqlalchemy import text
from datetime import datetime
from flask_cors import CORS
from routes import api
from database.db import db
import logging
from config.base import DATABASE_URL, GOOGLE_APPLICATION_CREDENTIALS
from google.cloud import logging as cloud_logging


client = cloud_logging.Client()
client.setup_logging()
logging.info("Google Cloud Logging initialized.")
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

logging.info("Database initialized.")


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))  # Simple query to check DB connection
            logging.info("Database health check successful.")
        return jsonify(
            {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
