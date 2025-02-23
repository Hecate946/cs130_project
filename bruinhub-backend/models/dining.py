from datetime import datetime, timezone
from database.db import db


class DiningHall(db.Model):
    __tablename__ = "dining_halls"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    menu = db.Column(db.JSON, nullable=False)  # requires JSON support; otherwise use db.Text
    hours_today = db.Column(db.JSON, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class DiningCapacityHistory(db.Model):
    __tablename__ = "dining_capacity_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.Integer, db.ForeignKey("dining_halls.id", ondelete="CASCADE"), nullable=False)
    occupants = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
