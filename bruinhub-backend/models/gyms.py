from datetime import datetime, timezone
from database.db import db

class Gym(db.Model):
    """Represents a gym and its latest schedule."""
    __tablename__ = "gyms"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    regular_hours = db.Column(db.JSON, nullable=False)  # requires JSON support; otherwise use db.Text
    special_hours = db.Column(db.JSON, nullable=True)
    last_updated = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )


class GymCapacityHistory(db.Model):
    """Tracks historical capacity changes for gym zones."""
    __tablename__ = "gym_capacity_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gym_id = db.Column(db.Integer, db.ForeignKey("gyms.id"), nullable=False)
    zone_name = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )
