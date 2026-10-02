"""
Serializers for Trip planning inputs and responses.
"""
from rest_framework import serializers
from apps.trips.models import Trip


class TripPlanInputSerializer(serializers.Serializer):
    """Input payload for planning a commercial trip."""
    current_location = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Current starting location or city (e.g. 'Chicago, IL')"
    )
    pickup_location = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Pickup / shipper location (e.g. 'Indianapolis, IN')"
    )
    dropoff_location = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Dropoff / consignee location (e.g. 'Dallas, TX')"
    )
    current_cycle_used = serializers.FloatField(
        required=True,
        min_value=0.0,
        max_value=70.0,
        help_text="Current cumulative on-duty cycle hours used out of 70 (e.g. 15.5)"
    )
    start_datetime = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Optional scheduled trip start datetime"
    )
    carrier_name = serializers.CharField(
        required=False,
        default="Spotter Freight Lines Inc.",
        max_length=255
    )
    truck_number = serializers.CharField(
        required=False,
        default="TRK-4091",
        max_length=50
    )
    trailer_number = serializers.CharField(
        required=False,
        default="TLR-8820",
        max_length=50
    )

    def validate_current_location(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Current location cannot be blank.")
        return val

    def validate_pickup_location(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Pickup location cannot be blank.")
        return val

    def validate_dropoff_location(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Dropoff location cannot be blank.")
        return val


class TripModelSerializer(serializers.ModelSerializer):
    """Serializer for saved trips."""
    class Meta:
        model = Trip
        fields = [
            "id",
            "origin_name",
            "pickup_name",
            "dropoff_name",
            "initial_cycle_used",
            "total_distance_miles",
            "total_driving_hours",
            "total_on_duty_hours",
            "total_trip_days",
            "fuel_stops_count",
            "rest_stops_count",
            "carrier_name",
            "truck_number",
            "trailer_number",
            "summary_data",
            "route_geojson",
            "legs_data",
            "stops_data",
            "daily_logs_data",
            "created_at",
        ]


class GeocodeSuggestionSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, min_length=2)
