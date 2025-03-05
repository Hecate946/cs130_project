#!/usr/bin/env python
import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from database.db import db
from models.notifications import DeviceToken
from services.notification_service import NotificationService
from config.base import DATABASE_URL

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
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "service": "notifications"})

@app.route('/api/notifications/register', methods=['POST'])
def register_device():
    """Register a new device for push notifications"""
    try:
        data = request.get_json()
        
        if not data or "pushToken" not in data:
            return jsonify({"error": "Missing required data: pushToken"}), 400
        
        push_token = data["pushToken"]
        device_type = data.get("deviceType", "unknown")
        user_id = data.get("userId")
        preferences = data.get("preferences")
        
        device = NotificationService.register_device(
            push_token=push_token,
            device_type=device_type,
            user_id=user_id,
            preferences=preferences
        )
        
        return jsonify({
            "message": "Device registered successfully",
            "deviceId": device.id,
            "preferences": device.preferences
        })
        
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/update-preferences', methods=['POST'])
def update_preferences():
    """Update notification preferences for a device"""
    try:
        data = request.get_json()
        
        if not data or "pushToken" not in data or "preferences" not in data:
            return jsonify({"error": "Missing required data: pushToken or preferences"}), 400
        
        push_token = data["pushToken"]
        preferences = data["preferences"]
        
        device = NotificationService.update_preferences(
            push_token=push_token,
            preferences=preferences
        )
        
        if not device:
            return jsonify({"error": "Device not found"}), 404
            
        return jsonify({
            "message": "Preferences updated successfully",
            "preferences": device.preferences
        })
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/notifications/simulate-event', methods=['POST'])
def simulate_event():
    """
    Simulate a notification event (capacity change or closing time)
    This endpoint is used for testing the notification triggers
    """
    try:
        data = request.get_json()
        
        if not data or "eventType" not in data or "facilityName" not in data:
            return jsonify({"error": "Missing required data: eventType or facilityName"}), 400
        
        event_type = data["eventType"]
        facility_name = data["facilityName"]
        
        if event_type == "capacity":
            if "currentCapacity" not in data:
                return jsonify({"error": "Missing required data: currentCapacity"}), 400
                
            current_capacity = data["currentCapacity"]
            responses = NotificationService.check_capacity_trigger(
                facility_name=facility_name,
                current_capacity=current_capacity
            )
            
            return jsonify({
                "message": f"Capacity event simulated for {facility_name}",
                "notifications_sent": len(responses),
                "responses": responses
            })
            
        elif event_type == "closing":
            if "minutesUntilClose" not in data:
                return jsonify({"error": "Missing required data: minutesUntilClose"}), 400
                
            minutes_until_close = data["minutesUntilClose"]
            responses = NotificationService.check_closing_trigger(
                facility_name=facility_name,
                minutes_until_close=minutes_until_close
            )
            
            return jsonify({
                "message": f"Closing event simulated for {facility_name}",
                "notifications_sent": len(responses),
                "responses": responses
            })
            
        else:
            return jsonify({"error": f"Invalid event type: {event_type}"}), 400
            
    except Exception as e:
        logger.error(f"Error simulating event: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Create the tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    # Run the app
    app.run(debug=True, host="0.0.0.0", port=5002)  # Different port from main API 