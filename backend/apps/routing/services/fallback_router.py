"""
Resilient fallback routing engine.
Computes road-adjusted distances, realistic driving times at commercial truck speeds,
and generates interpolated polyline coordinates.
"""
from typing import List
from apps.common.constants import DEFAULT_AVERAGE_SPEED_MPH, MILES_PER_METER
from apps.common.utils import haversine_distance_miles, road_distance_estimate_miles, interpolate_coordinates
from apps.routing.domain.coordinates import Coordinates
from apps.routing.domain.route import RouteLeg


class FallbackRouter:
    """Fallback router when external routing engines are unreachable or rate-limited."""

    @classmethod
    def calculate_leg(
        cls,
        origin_coord: Coordinates,
        dest_coord: Coordinates,
        origin_name: str = "",
        dest_name: str = "",
    ) -> RouteLeg:
        """Generate a realistic commercial route leg between two coordinates."""
        straight_line = haversine_distance_miles(
            origin_coord.latitude, origin_coord.longitude,
            dest_coord.latitude, dest_coord.longitude
        )
        road_miles = road_distance_estimate_miles(straight_line)
        # Avoid zero distance if same location
        road_miles = max(0.5, road_miles)

        driving_hours = road_miles / DEFAULT_AVERAGE_SPEED_MPH

        # Generate smooth polyline coordinates (e.g., 20 intermediate points)
        num_points = max(10, min(50, int(road_miles / 20)))
        coords_list: List[List[float]] = []

        coord_a = (origin_coord.latitude, origin_coord.longitude)
        coord_b = (dest_coord.latitude, dest_coord.longitude)

        for i in range(num_points + 1):
            fraction = i / float(num_points)
            lat, lon = interpolate_coordinates(coord_a, coord_b, fraction)
            coords_list.append([round(lon, 5), round(lat, 5)])  # GeoJSON is [lon, lat]

        return RouteLeg(
            origin_name=origin_name,
            destination_name=dest_name,
            origin_coord=origin_coord,
            destination_coord=dest_coord,
            distance_miles=round(road_miles, 1),
            duration_hours=round(driving_hours, 2),
            coordinates=coords_list
        )
