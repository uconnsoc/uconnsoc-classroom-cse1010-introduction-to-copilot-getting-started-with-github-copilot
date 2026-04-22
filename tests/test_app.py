import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9
    # Check structure of one activity
    activity = next(iter(data.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success(client):
    response = client.post("/activities/Debate%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Debate Team"]["participants"]


def test_signup_already_signed(client):
    # First signup
    client.post("/activities/Debate%20Team/signup?email=test@example.com")
    # Second signup should fail
    response = client.post("/activities/Debate%20Team/signup?email=test@example.com")
    assert response.status_code == 400


def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404


def test_delete_success(client):
    # First signup
    client.post("/activities/Debate%20Team/signup?email=test@example.com")
    # Then delete
    response = client.delete("/activities/Debate%20Team/signup/test@example.com")
    assert response.status_code == 200
    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" not in data["Debate Team"]["participants"]


def test_delete_participant_not_found(client):
    response = client.delete("/activities/Debate%20Team/signup/nonexistent@example.com")
    assert response.status_code == 404


def test_delete_activity_not_found(client):
    response = client.delete("/activities/Nonexistent/signup/test@example.com")
    assert response.status_code == 404


def test_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # RedirectResponse
    assert "/static/index.html" in response.headers.get("location", "")