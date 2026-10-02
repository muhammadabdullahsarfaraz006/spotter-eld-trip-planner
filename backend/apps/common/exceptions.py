"""
Custom exception hierarchy for the trip planner and HOS engine.
Provides clear, actionable error messages suitable for user presentation.
"""
from rest_framework.exceptions import APIException
from rest_framework import status


class TripPlannerException(APIException):
    """Base exception for trip planning and HOS domain errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred while planning the trip."
    default_code = "trip_planner_error"


class GeocodingException(TripPlannerException):
    """Raised when geocoding a location name or address fails."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = (
        "We could not resolve the specified location. "
        "Please check the city, state, or address and try again."
    )
    default_code = "geocoding_failed"


class RouteCalculationException(TripPlannerException):
    """Raised when the routing service cannot compute a path between waypoints."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = (
        "We couldn't calculate a driving route for the provided locations. "
        "Please verify that road connectivity exists between the points."
    )
    default_code = "route_calculation_failed"


class HOSViolationException(TripPlannerException):
    """Raised when an operation would force an unresolvable HOS violation."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The requested trip parameters exceed allowable Hours of Service limits."
    default_code = "hos_violation"


class InvalidCycleHoursException(TripPlannerException):
    """Raised when initial cycle hours used are outside realistic bounds."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Current cycle used must be between 0.0 and 70.0 hours."
    default_code = "invalid_cycle_hours"
