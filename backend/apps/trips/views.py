"""
API Views for Trip Planning, Geocoding Suggestions, and History.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination

from apps.common.exceptions import (
    TripPlannerException,
    GeocodingException,
    RouteCalculationException,
)
from apps.routing.services.geocoding_service import GeocodingService, KNOWN_US_LOCATIONS
from apps.hos.services.trip_scheduler import TripScheduler
from apps.trips.models import Trip
from apps.trips.serializers import (
    TripPlanInputSerializer,
    TripModelSerializer,
    GeocodeSuggestionSerializer,
)

logger = logging.getLogger(__name__)


class PlanTripAPIView(APIView):
    """
    POST /api/trips/plan/
    Receives trip details:
    - current_location (str)
    - pickup_location (str)
    - dropoff_location (str)
    - current_cycle_used (float)
    Outputs:
    - Map route instructions and GeoJSON geometry
    - Chronological list of stops, fuelings, rest breaks, and overnight sleeper berth rests
    - Standard FMCSA 24-hour Daily Log Sheets with step line coordinates and totals
    - Compliance and summary metrics
    """

    def post(self, request, *args, **kwargs):
        serializer = TripPlanInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors,
                    "message": "Please correct the form errors and try again."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        try:
            # 1. Geocode locations
            current_loc = GeocodingService.resolve_location(data["current_location"])
            pickup_loc = GeocodingService.resolve_location(data["pickup_location"])
            dropoff_loc = GeocodingService.resolve_location(data["dropoff_location"])

            # 2. Schedule trip & generate HOS daily logs
            result = TripScheduler.schedule_trip(
                current_loc=current_loc,
                pickup_loc=pickup_loc,
                dropoff_loc=dropoff_loc,
                current_cycle_used=data["current_cycle_used"],
                trip_start_datetime=data.get("start_datetime"),
                truck_number=data.get("truck_number", "TRK-4091"),
                trailer_number=data.get("trailer_number", "TLR-8820"),
                carrier_name=data.get("carrier_name", "Spotter Freight Lines Inc."),
            )

            # 3. Persist trip to database
            trip_record = Trip.objects.create(
                origin_name=current_loc.name,
                pickup_name=pickup_loc.name,
                dropoff_name=dropoff_loc.name,
                initial_cycle_used=data["current_cycle_used"],
                total_distance_miles=result["summary"]["total_distance_miles"],
                total_driving_hours=result["summary"]["total_driving_hours"],
                total_on_duty_hours=result["summary"]["total_on_duty_hours"],
                total_sleeper_hours=result["summary"]["total_sleeper_hours"],
                total_off_duty_hours=result["summary"]["total_off_duty_hours"],
                total_trip_days=result["summary"]["total_trip_days"],
                fuel_stops_count=result["summary"]["fuel_stops_count"],
                rest_stops_count=result["summary"]["rest_stops_count"],
                carrier_name=data.get("carrier_name", "Spotter Freight Lines Inc."),
                truck_number=data.get("truck_number", "TRK-4091"),
                trailer_number=data.get("trailer_number", "TLR-8820"),
                summary_data=result["summary"],
                route_geojson=result["route"]["geojson"],
                legs_data=result["route"]["legs"],
                stops_data=result["stops"],
                daily_logs_data=result["daily_logs"],
            )

            response_data = {
                "id": trip_record.id,
                "summary": result["summary"],
                "route": result["route"],
                "stops": result["stops"],
                "daily_logs": result["daily_logs"],
                "created_at": trip_record.created_at.isoformat(),
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except TripPlannerException as exc:
            logger.warning(f"Trip planning domain error: {exc}")
            return Response(
                {"error": exc.default_code, "message": str(exc.detail)},
                status=exc.status_code
            )
        except Exception as exc:
            logger.exception("Unexpected error while planning trip")
            return Response(
                {
                    "error": "server_error",
                    "message": "We encountered an unexpected issue while calculating your trip. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TripListAPIView(generics.ListAPIView):
    """GET /api/trips/ - Retrieve recent planned trips."""
    queryset = Trip.objects.all().order_by("-created_at")
    serializer_class = TripModelSerializer
    pagination_class = PageNumberPagination


class TripDetailAPIView(generics.RetrieveAPIView):
    """GET /api/trips/<id>/ - Retrieve details of a saved trip."""
    queryset = Trip.objects.all()
    serializer_class = TripModelSerializer
    lookup_field = "id"


class GeocodeSuggestAPIView(APIView):
    """
    GET /api/trips/suggest/?q=chi
    Returns quick city autocomplete suggestions for freight hubs.
    """
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "").strip().lower()
        if not query or len(query) < 2:
            return Response([])

        results = []
        for key, val in KNOWN_US_LOCATIONS.items():
            if query in key or query in val["name"].lower():
                results.append({
                    "name": val["name"],
                    "latitude": val["lat"],
                    "longitude": val["lon"],
                    "state": val.get("state", ""),
                })
                if len(results) >= 8:
                    break

        return Response(results)


class HealthCheckAPIView(APIView):
    """GET /api/health/ - Application health check."""
    def get(self, request, *args, **kwargs):
        return Response({
            "status": "healthy",
            "service": "Spotter ELD & HOS Trip Planner",
            "version": "1.0.0",
        })
