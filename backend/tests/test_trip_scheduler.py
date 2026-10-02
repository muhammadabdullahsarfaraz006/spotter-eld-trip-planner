"""
Unit tests for TripScheduler and 24-hour daily log partitioning.
"""
from apps.routing.domain.coordinates import Coordinates
from apps.routing.domain.route import Location
from apps.hos.services.trip_scheduler import TripScheduler


def test_short_trip_generates_valid_logs():
    current_loc = Location("Chicago, IL", Coordinates(41.8781, -87.6298))
    pickup_loc = Location("Gary, IN", Coordinates(41.5934, -87.3464))
    dropoff_loc = Location("Indianapolis, IN", Coordinates(39.7684, -86.1581))

    result = TripScheduler.schedule_trip(
        current_loc=current_loc,
        pickup_loc=pickup_loc,
        dropoff_loc=dropoff_loc,
        current_cycle_used=12.0
    )

    daily_logs = result["daily_logs"]
    assert len(daily_logs) >= 1

    # Every daily log must sum to exactly 24.0 hours
    for log in daily_logs:
        total = log["totals"]["total_hours"]
        assert abs(total - 24.0) < 0.1, f"Day {log['day_number']} total is {total}, expected 24.0"


def test_long_trip_enforces_fueling_every_1000_miles():
    current_loc = Location("Chicago, IL", Coordinates(41.8781, -87.6298))
    pickup_loc = Location("Indianapolis, IN", Coordinates(39.7684, -86.1581))
    dropoff_loc = Location("Dallas, TX", Coordinates(32.7767, -96.7970))

    result = TripScheduler.schedule_trip(
        current_loc=current_loc,
        pickup_loc=pickup_loc,
        dropoff_loc=dropoff_loc,
        current_cycle_used=5.0
    )

    summary = result["summary"]
    assert summary["total_distance_miles"] > 1000.0
    assert summary["fuel_stops_count"] >= 1

    stops = result["stops"]
    fuel_stops = [s for s in stops if s["stop_type"] == "FUEL"]
    assert len(fuel_stops) >= 1


def test_cross_country_trip_multi_day_24_hour_invariant():
    current_loc = Location("New York, NY", Coordinates(40.7128, -74.0060))
    pickup_loc = Location("Chicago, IL", Coordinates(41.8781, -87.6298))
    dropoff_loc = Location("Los Angeles, CA", Coordinates(34.0522, -118.2437))

    result = TripScheduler.schedule_trip(
        current_loc=current_loc,
        pickup_loc=pickup_loc,
        dropoff_loc=dropoff_loc,
        current_cycle_used=10.0
    )

    daily_logs = result["daily_logs"]
    assert len(daily_logs) >= 4

    for log in daily_logs:
        total = log["totals"]["total_hours"]
        assert abs(total - 24.0) < 0.1, f"Day {log['day_number']} total is {total}, expected 24.0"

    assert result["summary"]["rest_stops_count"] >= 4
    assert result["summary"]["fuel_stops_count"] >= 2
