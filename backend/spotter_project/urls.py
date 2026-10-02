"""
Root URL configuration for spotter_project.
"""
from django.contrib import admin
from django.urls import path, include
from apps.trips.views import HealthCheckAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckAPIView.as_view(), name="health-check"),
    path("api/trips/", include("apps.trips.urls", namespace="trips")),
]
