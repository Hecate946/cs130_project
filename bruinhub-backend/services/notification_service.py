import requests
import logging
import time
import json
from typing import List, Dict, Any, Optional
from database.db import db
from models.notifications import DeviceToken

# Configure logging
logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for managing and dispatching push notifications.
    Handles device token registration and notification dispatching.
    """
    
    @staticmethod
    def register_device(push_token: str, device_type: str, user_id: Optional[int] = None, 
                       preferences: Optional[Dict[str, Any]] = None, is_active: bool = True) -> DeviceToken:
        """
        Register or update a device token in the database.
        
        Args:
            push_token: The Expo push token
            device_type: The device type (ios, android)
            user_id: Optional user ID if available
            preferences: Optional notification preferences
            is_active: Whether notifications are globally enabled for this device
            
        Returns:
            The created or updated DeviceToken instance
        """
        try:
            # Check if token already exists
            existing_token = DeviceToken.query.filter_by(push_token=push_token).first()
            
            if existing_token:
                # Update existing token
                if user_id:
                    existing_token.user_id = user_id
                if preferences:
                    existing_token.preferences = preferences
                existing_token.device_type = device_type
                existing_token.is_active = is_active
                db.session.commit()
                logger.info(f"Updated existing device token: {push_token[:10]}...")
                return existing_token
            else:
                # Create new token
                new_token = DeviceToken(
                    push_token=push_token,
                    device_type=device_type,
                    user_id=user_id,
                    preferences=preferences,
                    is_active=is_active
                )
                db.session.add(new_token)
                db.session.commit()
                logger.info(f"Registered new device token: {push_token[:10]}...")
                return new_token
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering device token: {str(e)}")
            raise
    
    @staticmethod
    def update_preferences(push_token: str, preferences: Dict[str, Any]) -> Optional[DeviceToken]:
        """
        Update notification preferences for a device.
        
        Args:
            push_token: The Expo push token
            preferences: New notification preferences
            
        Returns:
            Updated DeviceToken instance or None if not found
        """
        try:
            device = DeviceToken.query.filter_by(push_token=push_token).first()
            if not device:
                logger.warning(f"Device token not found: {push_token[:10]}...")
                return None
                
            device.preferences = preferences
            db.session.commit()
            logger.info(f"Updated preferences for device: {push_token[:10]}...")
            return device
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating device preferences: {str(e)}")
            raise
    
    @staticmethod
    def dispatch_notification(push_token: str, title: str, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Dispatch a push notification to a specific device token.
        
        Args:
            push_token: The Expo push token
            title: The notification title
            message: The notification message
            data: Optional data payload for the notification
            
        Returns:
            Response from the Expo push API
        """
        try:
            logger.info(f"Dispatching notification to: {push_token[:10]}...")
            
            if not data:
                data = {}
                
            # Prepare the payload for Expo push API
            payload = {
                "to": push_token,
                "title": title,
                "body": message,
                "data": data,
                "sound": "default",
                "priority": "high"
            }
            
            # Send to Expo's Push API
            response = requests.post(
                "https://exp.host/--/api/v2/push/send",
                json=payload,
                headers={"Accept": "application/json", "Accept-encoding": "gzip, deflate"}
            )
            
            response_data = response.json()
            logger.info(f"Push notification response: {response_data}")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error dispatching notification: {str(e)}")
            # Return error information
            return {"error": str(e)}
    
    @staticmethod
    def check_capacity_trigger(facility_name: str, current_capacity: int) -> List[Dict[str, Any]]:
        """
        Check if any devices should be notified about a capacity change.
        
        Args:
            facility_name: The name of the facility
            current_capacity: The current capacity percentage
            
        Returns:
            List of dispatch responses
        """
        responses = []
        try:
            # Find active devices with capacity notifications enabled and matching threshold
            devices = DeviceToken.query.filter_by(is_active=True).all()
            eligible_devices = []
            
            for device in devices:
                preferences = device.preferences
                if (preferences.get("capacity", {}).get("enabled", False) and 
                    current_capacity <= preferences.get("capacity", {}).get("threshold", 50)):
                    eligible_devices.append(device)
            
            logger.info(f"Found {len(eligible_devices)} devices eligible for capacity notification")
            
            # Send notifications to eligible devices
            for device in eligible_devices:
                title = "BruinHub Capacity Alert"
                message = f"Alert: {facility_name} capacity is now {current_capacity}%."
                data = {
                    "type": "capacity",
                    "facility": facility_name,
                    "capacity": current_capacity
                }
                
                response = NotificationService.dispatch_notification(
                    device.push_token, title, message, data
                )
                responses.append(response)
                
            return responses
                
        except Exception as e:
            logger.error(f"Error processing capacity trigger: {str(e)}")
            return [{"error": str(e)}]
    
    @staticmethod
    def check_closing_trigger(facility_name: str, minutes_until_close: int) -> List[Dict[str, Any]]:
        """
        Check if any devices should be notified about a facility closing soon.
        
        Args:
            facility_name: The name of the facility
            minutes_until_close: Minutes until the facility closes
            
        Returns:
            List of dispatch responses
        """
        responses = []
        try:
            # Find active devices with closing notifications enabled and matching threshold
            devices = DeviceToken.query.filter_by(is_active=True).all()
            eligible_devices = []
            
            for device in devices:
                preferences = device.preferences
                if (preferences.get("closing", {}).get("enabled", False) and 
                    minutes_until_close <= preferences.get("closing", {}).get("minutes_before", 30)):
                    eligible_devices.append(device)
            
            logger.info(f"Found {len(eligible_devices)} devices eligible for closing notification")
            
            # Send notifications to eligible devices
            for device in eligible_devices:
                title = "BruinHub Closing Alert"
                message = f"Alert: {facility_name} will close in {minutes_until_close} minutes."
                data = {
                    "type": "closing",
                    "facility": facility_name,
                    "minutes_until_close": minutes_until_close
                }
                
                response = NotificationService.dispatch_notification(
                    device.push_token, title, message, data
                )
                responses.append(response)
                
            return responses
                
        except Exception as e:
            logger.error(f"Error processing closing trigger: {str(e)}")
            return [{"error": str(e)}]