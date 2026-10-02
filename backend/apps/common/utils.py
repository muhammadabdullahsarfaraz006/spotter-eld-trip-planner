"""
Utility functions for time, geometry, and unit calculations.
"""
import math
from datetime import datetime, timedelta
from typing import Tuple


def haversine_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points in miles using the Haversine formula.
    """
    earth_radius_miles = 3958.8  # Radius of earth in miles

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return earth_radius_miles * c


def road_distance_estimate_miles(straight_line_miles: float) -> float:
    """
    Estimate actual road highway driving distance from straight-line Haversine distance.
    Typical highway circuity factor in the US is roughly 1.15 to 1.25.
    """
    return straight_line_miles * 1.20


def round_to_nearest_quarter_hour(dt: datetime) -> datetime:
    """
    Round a datetime object to the nearest 15-minute mark (FMCSA log resolution).
    """
    minute = dt.minute
    second = dt.second
    microsecond = dt.microsecond

    # Total seconds past the hour
    total_seconds = minute * 60 + second + microsecond / 1e6
    quarter_seconds = 15 * 60

    # Nearest quarter
    nearest_quarter = round(total_seconds / quarter_seconds) * quarter_seconds
    base_hour = dt.replace(minute=0, second=0, microsecond=0)
    return base_hour + timedelta(seconds=nearest_quarter)


def format_hours_minutes(hours: float) -> str:
    """
    Format a decimal hour value to human-readable string like '10h 30m'.
    """
    if hours is None:
        return "0h 0m"
    total_minutes = int(round(hours * 60))
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m}m"


def interpolate_coordinates(
    coord1: Tuple[float, float],
    coord2: Tuple[float, float],
    fraction: float
) -> Tuple[float, float]:
    """
    Linearly interpolate between two (lat, lon) coordinates by fraction [0.0, 1.0].
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return (
        lat1 + (lat2 - lat1) * fraction,
        lon1 + (lon2 - lon1) * fraction
    )
