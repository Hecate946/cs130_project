from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Gym:
    id: int
    name: str
    slug: str
    last_updated: datetime

@dataclass
class GymZoneSnapshot:
    id: int
    gym_id: int
    snapshot_time: datetime
    zones: List[Dict]

@dataclass
class GymHoursSnapshot:
    id: int
    gym_id: int
    snapshot_time: datetime
    regular_hours: Dict[str, str]
    special_hours: Optional[Dict[str, str]] 