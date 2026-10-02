"""
Routing domain entities and data structures.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from .coordinates import Coordinates


class StopType(str, Enum):
    START = "START"
    PICKUP = "PICKUP"
    DROPOFF = "DROPOFF"
    FUEL = "FUEL"
    REST_BREAK = "REST_BREAK"
    SLEEPER_BERTH = "SLEEPER_BERTH"


@dataclass
class Location:
    name: str
    coordinates: Coordinates
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


@dataclass
class RouteStop:
    stop_type: StopType
    name: str
    coordinates: Coordinates
    arrival_time: datetime
    departure_time: datetime
    duration_hours: float
    cumulative_miles: float
    remark: str
    address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stop_type": self.stop_type.value,
            "name": self.name,
            "coordinates": {
                "latitude": self.coordinates.latitude,
                "longitude": self.coordinates.longitude,
            },
            "arrival_time": self.arrival_time.isoformat(),
            "departure_time": self.departure_time.isoformat(),
            "duration_hours": round(self.duration_hours, 2),
            "cumulative_miles": round(self.cumulative_miles, 1),
            "remark": self.remark,
            "address": self.address,
        }


@dataclass
class RouteLeg:
    origin_name: str
    destination_name: str
    origin_coord: Coordinates
    destination_coord: Coordinates
    distance_miles: float
    duration_hours: float
    coordinates: List[List[float]] = field(default_factory=list)  # [[lon, lat], ...]


@dataclass
class RouteResult:
    total_distance_miles: float
    total_driving_hours: float
    legs: List[RouteLeg] = field(default_factory=list)
    geometry_geojson: Dict[str, Any] = field(default_factory=dict)
