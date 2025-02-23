from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class DiningHall:
    """Represents a dining hall with its latest data."""

    id: int
    slug: str
    menu: Dict[str, list]  # Station -> List of items
    hours_today: Dict[str, str]
    last_updated: datetime


@dataclass
class DiningCapacityHistory:
    """Tracks historical capacity and occupancy changes for a dining hall."""

    id: int
    slug: str
    occupants: int
    capacity: int
    last_updated: datetime
