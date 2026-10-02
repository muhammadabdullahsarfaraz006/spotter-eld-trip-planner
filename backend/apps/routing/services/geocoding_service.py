"""
Geocoding service with multi-tier resolution:
1. In-memory cache
2. Pre-populated US logistics hubs dictionary
3. OpenStreetMap Nominatim API with resilient timeout & fallback
"""
import logging
import urllib.parse
import requests
from typing import Optional, Dict
from apps.common.exceptions import GeocodingException
from apps.routing.domain.coordinates import Coordinates
from apps.routing.domain.route import Location

logger = logging.getLogger(__name__)

# Pre-populated coordinates for top US freight and logistics hubs
KNOWN_US_LOCATIONS: Dict[str, Dict[str, float]] = {
    "chicago": {"lat": 41.8781, "lon": -87.6298, "state": "IL", "name": "Chicago, IL"},
    "indianapolis": {"lat": 39.7684, "lon": -86.1581, "state": "IN", "name": "Indianapolis, IN"},
    "dallas": {"lat": 32.7767, "lon": -96.7970, "state": "TX", "name": "Dallas, TX"},
    "fort worth": {"lat": 32.7555, "lon": -97.3308, "state": "TX", "name": "Fort Worth, TX"},
    "houston": {"lat": 29.7604, "lon": -95.3698, "state": "TX", "name": "Houston, TX"},
    "atlanta": {"lat": 33.7490, "lon": -84.3880, "state": "GA", "name": "Atlanta, GA"},
    "los angeles": {"lat": 34.0522, "lon": -118.2437, "state": "CA", "name": "Los Angeles, CA"},
    "long beach": {"lat": 33.7701, "lon": -118.1937, "state": "CA", "name": "Long Beach, CA"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "state": "NY", "name": "New York, NY"},
    "newark": {"lat": 40.7357, "lon": -74.1724, "state": "NJ", "name": "Newark, NJ"},
    "philadelphia": {"lat": 39.9526, "lon": -75.1652, "state": "PA", "name": "Philadelphia, PA"},
    "memphis": {"lat": 35.1495, "lon": -90.0490, "state": "TN", "name": "Memphis, TN"},
    "nashville": {"lat": 36.1627, "lon": -86.7816, "state": "TN", "name": "Nashville, TN"},
    "kansas city": {"lat": 39.0997, "lon": -94.5786, "state": "MO", "name": "Kansas City, MO"},
    "st. louis": {"lat": 38.6270, "lon": -90.1994, "state": "MO", "name": "St. Louis, MO"},
    "columbus": {"lat": 39.9612, "lon": -82.9988, "state": "OH", "name": "Columbus, OH"},
    "cincinnati": {"lat": 39.1031, "lon": -84.5120, "state": "OH", "name": "Cincinnati, OH"},
    "cleveland": {"lat": 41.4993, "lon": -81.6944, "state": "OH", "name": "Cleveland, OH"},
    "detroit": {"lat": 42.3314, "lon": -83.0458, "state": "MI", "name": "Detroit, MI"},
    "denver": {"lat": 39.7392, "lon": -104.9903, "state": "CO", "name": "Denver, CO"},
    "phoenix": {"lat": 33.4484, "lon": -112.0740, "state": "AZ", "name": "Phoenix, AZ"},
    "seattle": {"lat": 47.6062, "lon": -122.3321, "state": "WA", "name": "Seattle, WA"},
    "portland": {"lat": 45.5152, "lon": -122.6784, "state": "OR", "name": "Portland, OR"},
    "salt lake city": {"lat": 40.7608, "lon": -111.8910, "state": "UT", "name": "Salt Lake City, UT"},
    "miami": {"lat": 25.7617, "lon": -80.1918, "state": "FL", "name": "Miami, FL"},
    "jacksonville": {"lat": 30.3322, "lon": -81.6557, "state": "FL", "name": "Jacksonville, FL"},
    "charlotte": {"lat": 35.2271, "lon": -80.8431, "state": "NC", "name": "Charlotte, NC"},
    "louisville": {"lat": 38.2527, "lon": -85.7585, "state": "KY", "name": "Louisville, KY"},
    "minneapolis": {"lat": 44.9778, "lon": -93.2650, "state": "MN", "name": "Minneapolis, MN"},
    "omaha": {"lat": 41.2565, "lon": -95.9345, "state": "NE", "name": "Omaha, NE"},
    "albuquerque": {"lat": 35.0844, "lon": -106.6504, "state": "NM", "name": "Albuquerque, NM"},
    "oklahoma city": {"lat": 35.4676, "lon": -97.5164, "state": "OK", "name": "Oklahoma City, OK"},
    "little rock": {"lat": 34.7465, "lon": -92.2896, "state": "AR", "name": "Little Rock, AR"},
    "birmingham": {"lat": 33.5186, "lon": -86.8104, "state": "AL", "name": "Birmingham, AL"},
    "pittsburgh": {"lat": 40.4406, "lon": -79.9959, "state": "PA", "name": "Pittsburgh, PA"},
    "effingham": {"lat": 39.1200, "lon": -88.5434, "state": "IL", "name": "Effingham, IL"},
    "springfield": {"lat": 37.2090, "lon": -93.2923, "state": "MO", "name": "Springfield, MO"},
    "tulsa": {"lat": 36.1540, "lon": -95.9928, "state": "OK", "name": "Tulsa, OK"},
    "el paso": {"lat": 31.7619, "lon": -106.4850, "state": "TX", "name": "El Paso, TX"},
    "san antonio": {"lat": 29.4241, "lon": -98.4936, "state": "TX", "name": "San Antonio, TX"},
}


class GeocodingService:
    """Service to resolve place names or addresses into geographical coordinates."""

    _cache: Dict[str, Location] = {}

    @classmethod
    def resolve_location(cls, query: str) -> Location:
        """
        Resolve a location string into a Location domain entity.
        Raises GeocodingException if resolution fails.
        """
        clean_query = query.strip()
        if not clean_query:
            raise GeocodingException("Location query cannot be empty.")

        cache_key = clean_query.lower()
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # 1. Check known hubs dictionary (matches city name or part of query)
        for hub_key, hub_data in KNOWN_US_LOCATIONS.items():
            if hub_key in cache_key:
                location = Location(
                    name=clean_query,
                    coordinates=Coordinates(latitude=hub_data["lat"], longitude=hub_data["lon"]),
                    address=hub_data["name"],
                    state=hub_data.get("state"),
                )
                cls._cache[cache_key] = location
                return location

        # 2. Try OpenStreetMap Nominatim
        try:
            encoded_query = urllib.parse.quote(clean_query)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=1&countrycodes=us,ca,mx"
            headers = {"User-Agent": "Spotter-ELD-TripPlanner/1.0 (contact@assessment-spotter.local)"}

            response = requests.get(url, headers=headers, timeout=4.0)
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    first = results[0]
                    lat = float(first["lat"])
                    lon = float(first["lon"])
                    display_name = first.get("display_name", clean_query)
                    location = Location(
                        name=clean_query,
                        coordinates=Coordinates(latitude=lat, longitude=lon),
                        address=display_name,
                    )
                    cls._cache[cache_key] = location
                    return location
        except Exception as exc:
            logger.warning(f"Nominatim geocoding failed for '{clean_query}': {exc}")

        # If not found in known hubs or external API, check if user passed raw coords: "lat,lon"
        if "," in clean_query:
            parts = clean_query.split(",")
            if len(parts) == 2:
                try:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    location = Location(
                        name=f"Location ({lat:.4f}, {lon:.4f})",
                        coordinates=Coordinates(latitude=lat, longitude=lon),
                        address=f"{lat:.4f}, {lon:.4f}",
                    )
                    cls._cache[cache_key] = location
                    return location
                except ValueError:
                    pass

        raise GeocodingException(
            f"Could not locate '{clean_query}'. Please provide a valid US city (e.g. 'Chicago, IL') or address."
        )
