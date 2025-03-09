#!/usr/bin/env python
import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from database.db import db
from models.notifications import DeviceToken
from services.notification_service import NotificationService
from services.notification_scheduler import NotificationScheduler
from config.base import DATABASE_URL
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load configuration
DB_URL = DATABASE_URL
NOTIFICATION_INTERVAL = int(os.getenv("NOTIFICATION_INTERVAL", "3600"))
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "service": "notifications"})

@app.route('/api/notifications/check-now', methods=['POST'])
def trigger_notification_check():
    """
    Manually trigger a notification check for testing purposes.
    This endpoint will immediately run the capacity check for all facilities.
    """
    try:
        NotificationScheduler.check_and_notify()
        return jsonify({
            "message": "Notification check triggered successfully",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error triggering notification check: {str(e)}")
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/notifications/send-test', methods=['POST'])
def send_test():
    """Send a test notification to a device"""
    try:
        data = request.get_json()
        
        if not data or "pushToken" not in data:
            return jsonify({"error": "Missing required data: pushToken"}), 400
        
        push_token = data["pushToken"]
        title = data.get("title", "Test Notification")
        message = data.get("message", "This is a test notification from BruinHub!")
        custom_data = data.get("data", {})
        
        response = NotificationService.dispatch_notification(
            push_token=push_token,
            title=title,
            message=message,
            data=custom_data
        )
        
        return jsonify({
            "message": "Test notification sent",
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return jsonify({"error": str(e)}), 500

def init_scheduler():
    """Initialize the notification scheduler"""
    logger.info("Initializing notification scheduler")
    
    def check_with_context():
        """Wrapper to ensure app context is available"""
        with app.app_context():
            try:
                logger.info("Running scheduled capacity check")
                NotificationScheduler.check_and_notify()
                logger.info("Completed scheduled capacity check")
            except Exception as e:
                logger.error(f"Error in scheduled check: {str(e)}", exc_info=True)
    
    # Add job to check capacities every 5 minutes
    scheduler.add_job(
        func=check_with_context,
        trigger='interval',
        seconds=NOTIFICATION_INTERVAL,
        id='check_capacities'
    )
    
    scheduler.start()
    logger.info("Notification scheduler started")

if __name__ == "__main__":
    # Create the tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    # Initialize and start the scheduler
    init_scheduler()
    
    # Run the app
    app.run(debug=True, host="0.0.0.0", port=5002)  # Different port from main API 