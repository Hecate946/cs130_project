from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class Gym:
    """Represents a gym with its latest schedule."""
    id: int
    slug: str
    regular_hours: Dict[str, str]
    special_hours: Optional[Dict[str, str]]
    last_updated: datetime

@dataclass
class GymCapacityHistory:
    """Tracks historical capacity changes for gym zones."""
    id: int
    gym_id: int
    zone_name: str
    capacity: int
    percentage: int
    last_updated: datetime
