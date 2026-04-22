"""
Tests for the Mergington High School Activity Management API

Tests cover all endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- POST /activities/{activity_name}/remove
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


# ==================== GET /activities Tests ====================

class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that activity objects have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_list_populated(self, client, reset_activities):
        """Test that participants list is correctly populated"""
        response = client.get("/activities")
        data = response.json()
        
        chess_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        assert len(chess_participants) == 2


# ==================== POST /activities/{activity_name}/signup Tests ====================

class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities):
        """Test successfully signing up a new student"""
        response = client.post(
            "/activities/Chess Club/signup?email=alice@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alice@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post("/activities/Chess Club/signup?email=alice@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        assert "alice@mergington.edu" in participants
        assert len(participants) == 3  # 2 original + 1 new

    def test_signup_decreases_available_spots(self, client, reset_activities):
        """Test that signup decreases the number of available spots"""
        # Chess Club has max 12, currently 2 participants = 10 available
        response_before = client.get("/activities")
        max_before = response_before.json()["Chess Club"]["max_participants"]
        participants_before = len(response_before.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/signup?email=alice@mergington.edu")
        
        response_after = client.get("/activities")
        participants_after = len(response_after.json()["Chess Club"]["participants"])
        
        assert participants_after == participants_before + 1

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Non-Existent Club/signup?email=bob@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_rejected(self, client, reset_activities):
        """Test that duplicate signup is rejected with 400"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_different_student_same_activity(self, client, reset_activities):
        """Test multiple different students can sign up for same activity"""
        client.post("/activities/Chess Club/signup?email=alice@mergington.edu")
        response = client.post("/activities/Chess Club/signup?email=bob@mergington.edu")
        
        assert response.status_code == 200
        
        response_check = client.get("/activities")
        participants = response_check.json()["Chess Club"]["participants"]
        assert "alice@mergington.edu" in participants
        assert "bob@mergington.edu" in participants

    def test_signup_same_student_different_activities(self, client, reset_activities):
        """Test same student can sign up for multiple activities"""
        response1 = client.post("/activities/Chess Club/signup?email=alice@mergington.edu")
        response2 = client.post("/activities/Programming Class/signup?email=alice@mergington.edu")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response_check = client.get("/activities")
        data = response_check.json()
        assert "alice@mergington.edu" in data["Chess Club"]["participants"]
        assert "alice@mergington.edu" in data["Programming Class"]["participants"]


# ==================== POST /activities/{activity_name}/remove Tests ====================

class TestRemoveParticipant:
    """Tests for the POST /activities/{activity_name}/remove endpoint"""

    def test_remove_successful(self, client, reset_activities):
        """Test successfully removing a participant"""
        response = client.post(
            "/activities/Chess Club/remove?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_removes_participant_from_activity(self, client, reset_activities):
        """Test that remove actually removes the participant"""
        client.post("/activities/Chess Club/remove?email=michael@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" not in participants
        assert len(participants) == 1

    def test_remove_increases_available_spots(self, client, reset_activities):
        """Test that removing a participant increases available spots"""
        response_before = client.get("/activities")
        participants_before = len(response_before.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/remove?email=michael@mergington.edu")
        
        response_after = client.get("/activities")
        participants_after = len(response_after.json()["Chess Club"]["participants"])
        
        assert participants_after == participants_before - 1

    def test_remove_activity_not_found(self, client, reset_activities):
        """Test removing from non-existent activity returns 404"""
        response = client.post(
            "/activities/Non-Existent Club/remove?email=michael@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_student_not_registered(self, client, reset_activities):
        """Test removing student who is not registered returns 400"""
        response = client.post(
            "/activities/Chess Club/remove?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_remove_all_participants_one_by_one(self, client, reset_activities):
        """Test removing all participants from an activity"""
        # Gym Class has john and olivia
        response = client.get("/activities")
        initial_count = len(response.json()["Gym Class"]["participants"])
        assert initial_count == 2
        
        # Remove both
        client.post("/activities/Gym Class/remove?email=john@mergington.edu")
        client.post("/activities/Gym Class/remove?email=olivia@mergington.edu")
        
        response = client.get("/activities")
        final_count = len(response.json()["Gym Class"]["participants"])
        assert final_count == 0


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests covering multiple operations"""

    def test_signup_then_remove_workflow(self, client, reset_activities):
        """Test complete signup then remove workflow"""
        # Sign up new participant
        client.post("/activities/Chess Club/signup?email=alice@mergington.edu")
        
        response1 = client.get("/activities")
        assert "alice@mergington.edu" in response1.json()["Chess Club"]["participants"]
        
        # Remove the participant
        client.post("/activities/Chess Club/remove?email=alice@mergington.edu")
        
        response2 = client.get("/activities")
        assert "alice@mergington.edu" not in response2.json()["Chess Club"]["participants"]

    def test_multiple_operations_sequence(self, client, reset_activities):
        """Test multiple operations in sequence"""
        # Sign up multiple students
        client.post("/activities/Chess Club/signup?email=alice@mergington.edu")
        client.post("/activities/Chess Club/signup?email=bob@mergington.edu")
        client.post("/activities/Programming Class/signup?email=alice@mergington.edu")
        
        # Verify all three
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 4  # 2 original + 2 new
        assert len(data["Programming Class"]["participants"]) == 3  # 2 original + 1 new
        
        # Remove one from Chess Club
        client.post("/activities/Chess Club/remove?email=alice@mergington.edu")
        
        # Verify counts updated
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 3
        assert len(data["Programming Class"]["participants"]) == 3  # unchanged
