"""API integration and endpoint verification tests for AeroSanctuary AI.

Contains 20 comprehensive unit and integration tests verifying all REST endpoints,
status codes, parameter variations, payload schemas, and validation errors.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient fixture for FastAPI endpoints."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_check_endpoint(client):
    """Verifies that /api/health returns 200 OK and valid system metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "AeroSanctuary AI" in data["app_name"]


def test_health_check_headers(client):
    """Verifies that security headers are applied to health responses."""
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_aqi_endpoint_default(client):
    """Verifies AQI snapshot retrieval for default city (Delhi-NCR)."""
    response = client.get("/api/aqi")
    assert response.status_code == 200
    data = response.json()
    assert data["aqi"] > 0
    assert "pm25_ug_m3" in data
    assert "safest_outdoor_window" in data


def test_aqi_endpoint_delhi(client):
    """Verifies explicit Delhi-NCR air quality metrics."""
    response = client.get("/api/aqi?location=Delhi-NCR")
    assert response.status_code == 200
    data = response.json()
    assert "Delhi" in data["city"]
    assert data["aqi"] >= 300
    assert data["thermal_inversion_active"] is True


def test_aqi_endpoint_chandigarh(client):
    """Verifies Chandigarh air quality and inversion telemetry."""
    response = client.get("/api/aqi?location=Chandigarh")
    assert response.status_code == 200
    data = response.json()
    assert "Chandigarh" in data["city"]
    assert data["pm25_ug_m3"] > 100.0


def test_aqi_endpoint_mumbai(client):
    """Verifies coastal city air quality without thermal inversion."""
    response = client.get("/api/aqi?location=Mumbai")
    assert response.status_code == 200
    data = response.json()
    assert "Mumbai" in data["city"]
    assert data["thermal_inversion_active"] is False


def test_aqi_endpoint_lahore(client):
    """Verifies Lahore severe smog parameters."""
    response = client.get("/api/aqi?location=Lahore")
    assert response.status_code == 200
    data = response.json()
    assert "Lahore" in data["city"]
    assert data["aqi"] >= 400


def test_aqi_endpoint_beijing(client):
    """Verifies Beijing winter metrics."""
    response = client.get("/api/aqi?location=Beijing")
    assert response.status_code == 200
    data = response.json()
    assert "Beijing" in data["city"]


def test_aqi_endpoint_new_york(client):
    """Verifies low-baseline international benchmark city."""
    response = client.get("/api/aqi?location=New%20York")
    assert response.status_code == 200
    data = response.json()
    assert data["aqi"] < 100


def test_aqi_endpoint_london(client):
    """Verifies London moderate metrics."""
    response = client.get("/api/aqi?location=London")
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "Moderate (51-100)"


def test_aqi_endpoint_unknown_city(client):
    """Verifies modeled fallback for arbitrary unmapped locations."""
    response = client.get("/api/aqi?location=Metropolis")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Metropolis"
    assert data["aqi"] > 0


def test_indoor_hacks_all(client):
    """Verifies that the indoor hacks endpoint returns all curated solutions."""
    response = client.get("/api/indoor-hacks")
    assert response.status_code == 200
    hacks = response.json()
    assert len(hacks) == 4


def test_indoor_hacks_diy_filtration(client):
    """Verifies filtering by diy_filtration category."""
    response = client.get("/api/indoor-hacks?category=diy_filtration")
    assert response.status_code == 200
    hacks = response.json()
    assert len(hacks) == 1
    assert "Corsi-Rosenthal" in hacks[0]["title"]


def test_indoor_hacks_botanical(client):
    """Verifies filtering by botanical category."""
    response = client.get("/api/indoor-hacks?category=botanical")
    assert response.status_code == 200
    hacks = response.json()
    assert len(hacks) == 1
    assert "NASA" in hacks[0]["title"]


def test_indoor_hacks_ventilation_timing(client):
    """Verifies filtering by ventilation_timing category."""
    response = client.get("/api/indoor-hacks?category=ventilation_timing")
    assert response.status_code == 200
    hacks = response.json()
    assert len(hacks) == 1
    assert "Inversion" in hacks[0]["title"]


def test_indoor_hacks_source_control(client):
    """Verifies filtering by source_control category."""
    response = client.get("/api/indoor-hacks?category=source_control")
    assert response.status_code == 200
    hacks = response.json()
    assert len(hacks) == 1
    assert "Microfiber" in hacks[0]["title"]


def test_indoor_hacks_invalid_category(client):
    """Verifies that unknown hack categories return an empty list gracefully."""
    response = client.get("/api/indoor-hacks?category=space_lasers")
    assert response.status_code == 200
    assert response.json() == []


def test_generate_action_plan_endpoint(client):
    """Verifies end-to-end action plan generation for a typical urban family."""
    payload = {
        "location": "Delhi-NCR",
        "household_type": "family_with_kids",
        "commute_mode": "ice_car",
        "daily_commute_km": 20.0,
        "heating_source": "none_passive",
        "ventilation_habits": "Morning open windows",
        "air_purifier_owned": False,
    }
    response = client.post("/api/generate-plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "air_quality_snapshot" in data
    assert "daily_routine_schedule" in data
    assert "indoor_air_hacks" in data
    assert "impact_ledger" in data
    assert "genai_executive_summary" in data


def test_generate_action_plan_validation_error(client):
    """Verifies that invalid payloads trigger 422 Unprocessable Entity."""
    # Negative commute km is rejected by schema validator
    bad_payload = {
        "location": "Delhi",
        "daily_commute_km": -50.0,
    }
    response = client.post("/api/generate-plan", json=bad_payload)
    assert response.status_code == 422


def test_chat_consultation_endpoint(client):
    """Verifies interactive GenAI chat consultation endpoint."""
    payload = {
        "message": "How do I build a Corsi-Rosenthal box air purifier?",
        "user_profile": {
            "location": "Delhi-NCR",
            "household_type": "family_with_kids",
            "commute_mode": "ice_car",
            "daily_commute_km": 15.0,
        },
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "actionable_tips" in data
    assert "direct_impact_statement" in data


def test_generate_action_plan_boundary_commute_exact_limits(client):
    """Verifies that boundary commute distances (0.0 km and 200.0 km) succeed with 200 OK."""
    for boundary_km in [0.0, 200.0]:
        payload = {
            "location": "Delhi-NCR",
            "daily_commute_km": boundary_km,
        }
        response = client.post("/api/generate-plan", json=payload)
        assert response.status_code == 200
        assert response.json()["user_profile"]["daily_commute_km"] == boundary_km


def test_generate_action_plan_rejects_commute_over_limit(client):
    """Verifies that commute distances exceeding 200.0 km are rejected with 422."""
    payload = {
        "location": "Delhi-NCR",
        "daily_commute_km": 200.5,
    }
    response = client.post("/api/generate-plan", json=payload)
    assert response.status_code == 422


def test_generate_action_plan_rejects_empty_and_whitespace_location(client):
    """Verifies that empty string or whitespace-only locations are rejected with 422."""
    for bad_loc in ["", "   ", "\t\n"]:
        payload = {
            "location": bad_loc,
            "daily_commute_km": 15.0,
        }
        response = client.post("/api/generate-plan", json=payload)
        assert response.status_code == 422


def test_payload_size_limit_rejection_over_10kb(client):
    """Verifies that request bodies exceeding the 10 KB threshold trigger 413 Payload Too Large."""
    oversized_message = "A" * (12 * 1024)  # 12 KB payload
    payload = {"message": oversized_message}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 413
