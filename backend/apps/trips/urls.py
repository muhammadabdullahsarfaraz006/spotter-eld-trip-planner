"""
URL patterns for trips application.
"""
from django.urls import path
from apps.trips.views import (
    PlanTripAPIView,
    TripListAPIView,
    TripDetailAPIView,
    GeocodeSuggestAPIView,
)

app_name = "trips"

urlpatterns = [
    path("plan/", PlanTripAPIView.as_view(), name="plan-trip"),
    path("suggest/", GeocodeSuggestAPIView.as_view(), name="geocode-suggest"),
    path("", TripListAPIView.as_view(), name="trip-list"),
    path("<int:id>/", TripDetailAPIView.as_view(), name="trip-detail"),
]
