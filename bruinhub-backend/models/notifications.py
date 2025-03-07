from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database.db import db
import copy

class DeviceToken(db.Model):
    """
    Model to store Expo push notification tokens and user preferences for notifications.
    This allows for personalized notification preferences per device/user.
    """
    __tablename__ = 'device_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    push_token = Column(String(255), unique=True, nullable=False)
    device_type = Column(String(20), nullable=False)  # 'ios', 'android', etc.
    preferences = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    is_active = Column(Boolean, default=True)

    def __init__(self, push_token, device_type, user_id=None, preferences=None, is_active=True):
        self.push_token = push_token
        self.device_type = device_type
        self.user_id = user_id
        self.is_active = is_active
        
        # Set preferences with defaults only if none provided
        if preferences is None:
            self.preferences = {
                "capacity": {"enabled": True, "threshold": 50},
                "closing": {"enabled": True, "minutes_before": 30}
            }
        else:
            # Make a deep copy to ensure we don't have reference issues
            self.preferences = copy.deepcopy(preferences)
    
    def __repr__(self):
        return f"<DeviceToken id={self.id} push_token={self.push_token[:10]}...>" 