"""
Integration tests for Django REST Framework Trip API endpoints.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
def test_plan_trip_api_success():
    client = APIClient()
    payload = {
        "current_location": "Chicago, IL",
        "pickup_location": "Indianapolis, IN",
        "dropoff_location": "Dallas, TX",
        "current_cycle_used": 14.5,
    }

    response = client.post("/api/trips/plan/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "id" in data
    assert "summary" in data
    assert "route" in data
    assert "stops" in data
    assert "daily_logs" in data

    summary = data["summary"]
    assert summary["origin"] == "Chicago, IL"
    assert summary["pickup"] == "Indianapolis, IN"
    assert summary["dropoff"] == "Dallas, TX"
    assert summary["total_distance_miles"] > 900


@pytest.mark.django_db
def test_plan_trip_api_validation_failure():
    client = APIClient()
    # Missing dropoff location and negative cycle hours
    payload = {
        "current_location": "Chicago, IL",
        "pickup_location": "Indianapolis, IN",
        "current_cycle_used": -5.0,
    }

    response = client.post("/api/trips/plan/", payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "details" in data


@pytest.mark.django_db
def test_geocode_suggest_api():
    client = APIClient()
    response = client.get("/api/trips/suggest/?q=chic")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert "Chicago" in data[0]["name"]


@pytest.mark.django_db
def test_health_check_api():
    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"
