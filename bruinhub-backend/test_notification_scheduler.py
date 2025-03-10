#!/usr/bin/env python
"""
Script to insert a test device token with notification preferences for testing the scheduler.
"""

import logging
from flask import Flask
from database.db import db
from models.notifications import DeviceToken
from config.base import DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test push token (replace with a real Expo push token for actual testing)
TEST_PUSH_TOKEN = "ExponentPushToken[096EhAL5PBLxhjzeMijLfs]"

# Test preferences - enable notifications for some facilities with different thresholds
TEST_PREFERENCES = {
    "capacity": {
        # Dining halls
        "bplate": {"enabled": True, "threshold": 50},
        "deneve": {"enabled": True, "threshold": 75},
        "epicuria-covel": {"enabled": True, "threshold": 60},
        # Gyms
        "bfit": {"enabled": True, "threshold": 40},
        "john-wooden-center": {"enabled": True, "threshold": 80},
    }
}


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def insert_test_device():
    """Insert or update the test device with notification preferences."""
    try:
        # Check if device already exists
        device = DeviceToken.query.filter_by(push_token=TEST_PUSH_TOKEN).first()

        if device:
            logger.info("Updating existing test device")
            device.preferences = TEST_PREFERENCES
            device.is_active = True
        else:
            logger.info("Creating new test device")
            device = DeviceToken(
                push_token=TEST_PUSH_TOKEN,
                device_type="test",
                preferences=TEST_PREFERENCES,
            )
            db.session.add(device)

        db.session.commit()
        logger.info("Successfully inserted/updated test device")
        logger.info(f"Device ID: {device.id}")
        logger.info(f"Preferences: {device.preferences}")

    except Exception as e:
        logger.error(f"Error inserting test device: {str(e)}")
        db.session.rollback()
        raise


def main():
    """Main function to run the test script."""
    app = create_app()

    with app.app_context():
        logger.info("Starting test device insertion")
        insert_test_device()
        logger.info("Test setup complete")


if __name__ == "__main__":
    main()
