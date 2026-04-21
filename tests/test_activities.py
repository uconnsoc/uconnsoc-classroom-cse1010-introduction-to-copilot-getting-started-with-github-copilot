"""
Tests for the Mergington High School Activities API endpoints.
"""

import pytest


def test_get_activities(client, test_activities):
    """Test that GET /activities returns all activities with correct structure."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all activities are returned
    assert len(data) == 3
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Verify activity structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)
    
    # Verify current participants
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_signup_success(client, test_activities):
    """Test that a student can successfully sign up for an activity."""
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Verify participant is not already signed up
    assert email not in test_activities[activity_name]["participants"]
    initial_count = len(test_activities[activity_name]["participants"])
    
    # Sign up the student
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Verify successful response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify participant was added
    assert email in test_activities[activity_name]["participants"]
    assert len(test_activities[activity_name]["participants"]) == initial_count + 1


def test_unregister_success(client, test_activities):
    """Test that a student can successfully unregister from an activity."""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This student is already signed up
    
    # Verify participant is currently signed up
    assert email in test_activities[activity_name]["participants"]
    initial_count = len(test_activities[activity_name]["participants"])
    
    # Unregister the student
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    # Verify successful response
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify participant was removed
    assert email not in test_activities[activity_name]["participants"]
    assert len(test_activities[activity_name]["participants"]) == initial_count - 1
