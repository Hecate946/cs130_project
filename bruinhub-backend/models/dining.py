from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class DiningHall:
    id: int
    name: str
    capacity: int
    last_updated: datetime


@dataclass
class DiningMenuSnapshot:
    id: int
    hall_id: int
    snapshot_time: datetime
    menu: Dict[str, List[str]]  # Station name -> List of food items


@dataclass
class DiningHoursSnapshot:
    id: int
    hall_id: int
    snapshot_time: datetime
    regular_hours: Dict[str, str]
    special_hours: Optional[Dict[str, str]]  # Special hours for holidays, events, etc.
