"""Routes for managing notification preferences and device registration."""

import logging
from flask import Blueprint, request, jsonify
from models.notifications import DeviceToken
from services.notification_service import NotificationService
from database.db import db

logger = logging.getLogger(__name__)
notification_routes = Blueprint("notification_routes", __name__)

@notification_routes.route("/v1/notifications/register", methods=["POST"])
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
        is_active = data.get("is_active", True)  # Default to active
        
        device = NotificationService.register_device(
            push_token=push_token,
            device_type=device_type,
            user_id=user_id,
            preferences=preferences,
            is_active=is_active
        )
        
        return jsonify({
            "message": "Device registered successfully",
            "deviceId": device.id,
            "preferences": device.preferences,
            "is_active": device.is_active
        })
        
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        return jsonify({"error": str(e)}), 500

@notification_routes.route("/v1/notifications/update-preferences", methods=["POST"])
def update_preferences():
    """
    Update notification preferences for a device.
    Only updates the specified preferences, preserving existing ones.
    If device is not found, registers it first.
    """
    try:
        data = request.get_json()
        
        if not data or "pushToken" not in data or "preferences" not in data:
            return jsonify({"error": "Missing required data: pushToken or preferences"}), 400
        
        push_token = data["pushToken"]
        new_preferences = data["preferences"]
        is_active = data.get("is_active")  # This can be None if not provided
        
        # Get existing device
        device = DeviceToken.query.filter_by(push_token=push_token).first()
        
        # If device not found, register it first
        if not device:
            logger.info(f"Device {push_token[:10]}... not found, registering it")
            device = NotificationService.register_device(
                push_token=push_token,
                device_type=data.get("deviceType", "unknown"),
                user_id=data.get("userId"),
                preferences=new_preferences,
                is_active=is_active if is_active is not None else True
            )
            return jsonify({
                "message": "Device registered with preferences",
                "deviceId": device.id,
                "preferences": device.preferences,
                "is_active": device.is_active
            })
            
        # Get current preferences and make a deep copy
        current_preferences = dict(device.preferences or {})
        
        # Update capacity preferences if they exist in the new preferences
        if "capacity" in new_preferences:
            if "capacity" not in current_preferences:
                current_preferences["capacity"] = {}
                
            # Update each facility's preferences exactly as provided
            for facility, prefs in new_preferences["capacity"].items():
                facility_prefs = dict(prefs)
                current_preferences["capacity"][facility] = facility_prefs
        
        # Update directly in the database
        db.session.execute(
            db.update(DeviceToken)
            .where(DeviceToken.push_token == push_token)
            .values(
                preferences=current_preferences,
                is_active=is_active if is_active is not None else DeviceToken.is_active
            )
        )
        db.session.commit()
        
        # Get updated device
        saved_device = DeviceToken.query.filter_by(push_token=push_token).first()
            
        return jsonify({
            "message": "Preferences updated successfully",
            "preferences": saved_device.preferences,
            "is_active": saved_device.is_active
        })
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500 