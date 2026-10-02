"""
Persistence models for Trips and generated ELD logs.
"""
from django.db import models


class Trip(models.Model):
    """Stores planned trip details, route geometry, stops, and HOS log sheets."""
    origin_name = models.CharField(max_length=255)
    pickup_name = models.CharField(max_length=255)
    dropoff_name = models.CharField(max_length=255)
    initial_cycle_used = models.FloatField(default=0.0)

    # Metrics
    total_distance_miles = models.FloatField(default=0.0)
    total_driving_hours = models.FloatField(default=0.0)
    total_on_duty_hours = models.FloatField(default=0.0)
    total_sleeper_hours = models.FloatField(default=0.0)
    total_off_duty_hours = models.FloatField(default=0.0)
    total_trip_days = models.IntegerField(default=1)
    fuel_stops_count = models.IntegerField(default=0)
    rest_stops_count = models.IntegerField(default=0)

    # Carrier & Vehicle details
    carrier_name = models.CharField(max_length=255, default="Spotter Freight Lines Inc.")
    truck_number = models.CharField(max_length=50, default="TRK-4091")
    trailer_number = models.CharField(max_length=50, default="TLR-8820")

    # Structured Payloads
    summary_data = models.JSONField(default=dict)
    route_geojson = models.JSONField(default=dict)
    legs_data = models.JSONField(default=list)
    stops_data = models.JSONField(default=list)
    daily_logs_data = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    def __str__(self):
        return f"Trip {self.id}: {self.origin_name} -> {self.pickup_name} -> {self.dropoff_name} ({self.total_distance_miles:.1f} mi)"
