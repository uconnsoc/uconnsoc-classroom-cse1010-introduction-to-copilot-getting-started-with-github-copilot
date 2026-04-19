"""
Tests for activities endpoint
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client):
        """Should return 200 status and list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_fields(self, client):
        """Each activity should have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_contains_chess_club(self, client):
        """Response should include Chess Club"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities

    def test_activities_have_participant_list(self, client):
        """Each activity should have a list of participants"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            assert isinstance(activity_data["participants"], list)