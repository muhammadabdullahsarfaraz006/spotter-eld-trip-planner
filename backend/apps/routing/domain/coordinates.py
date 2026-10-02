"""
Coordinates Value Object.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"Latitude {self.latitude} must be between -90 and 90.")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"Longitude {self.longitude} must be between -180 and 180.")

    def as_tuple(self) -> Tuple[float, float]:
        """Return as (lat, lon)"""
        return (self.latitude, self.longitude)

    def as_geojson_coord(self) -> Tuple[float, float]:
        """Return as [lon, lat] per GeoJSON specification"""
        return (self.longitude, self.latitude)
