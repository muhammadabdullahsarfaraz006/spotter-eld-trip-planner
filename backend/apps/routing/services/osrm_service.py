"""
OSRM (Open Source Routing Machine) Client.
Fetches high-fidelity highway routes and turn-by-turn geometry.
Falls back seamlessly to FallbackRouter if unreachable.
"""
import logging
import requests
from typing import List
from apps.common.constants import METERS_PER_MILE
from apps.routing.domain.coordinates import Coordinates
from apps.routing.domain.route import RouteLeg, RouteResult
from .fallback_router import FallbackRouter

logger = logging.getLogger(__name__)

OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"


class OSRMRoutingService:
    """Service to calculate commercial driving routes using OSRM with automatic fallback."""

    @classmethod
    def get_route_leg(
        cls,
        origin: Coordinates,
        destination: Coordinates,
        origin_name: str = "",
        dest_name: str = "",
    ) -> RouteLeg:
        """Calculate a driving leg between two points."""
        coords_str = f"{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}"
        url = OSRM_ROUTE_URL.format(coords=coords_str)

        try:
            response = requests.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    primary_route = data["routes"][0]
                    distance_meters = primary_route.get("distance", 0.0)
                    duration_seconds = primary_route.get("duration", 0.0)
                    geometry = primary_route.get("geometry", {})
                    coordinates = geometry.get("coordinates", [])

                    distance_miles = distance_meters / METERS_PER_MILE
                    # Commercial trucks generally drive ~15% slower than passenger car OSRM estimates
                    duration_hours = (duration_seconds / 3600.0) * 1.12

                    return RouteLeg(
                        origin_name=origin_name,
                        destination_name=dest_name,
                        origin_coord=origin,
                        destination_coord=destination,
                        distance_miles=round(distance_miles, 1),
                        duration_hours=round(duration_hours, 2),
                        coordinates=coordinates,
                    )
        except Exception as exc:
            logger.info(f"OSRM request failed ({exc}). Using internal routing engine.")

        # Fallback
        return FallbackRouter.calculate_leg(
            origin_coord=origin,
            dest_coord=destination,
            origin_name=origin_name,
            dest_name=dest_name,
        )

    @classmethod
    def build_full_route(cls, waypoints: List[tuple]) -> RouteResult:
        """
        Build a multi-leg route across waypoints.
        waypoints is list of tuples: (name, Coordinates)
        """
        legs: List[RouteLeg] = []
        all_coords: List[List[float]] = []
        total_distance = 0.0
        total_duration = 0.0

        for i in range(len(waypoints) - 1):
            orig_name, orig_coord = waypoints[i]
            dest_name, dest_coord = waypoints[i + 1]

            leg = cls.get_route_leg(orig_coord, dest_coord, orig_name, dest_name)
            legs.append(leg)
            total_distance += leg.distance_miles
            total_duration += leg.duration_hours

            # Combine GeoJSON polyline coords
            if leg.coordinates:
                if all_coords and leg.coordinates and all_coords[-1] == leg.coordinates[0]:
                    all_coords.extend(leg.coordinates[1:])
                else:
                    all_coords.extend(leg.coordinates)

        geojson_geometry = {
            "type": "LineString",
            "coordinates": all_coords
        }

        return RouteResult(
            total_distance_miles=round(total_distance, 1),
            total_driving_hours=round(total_duration, 2),
            legs=legs,
            geometry_geojson=geojson_geometry,
        )
