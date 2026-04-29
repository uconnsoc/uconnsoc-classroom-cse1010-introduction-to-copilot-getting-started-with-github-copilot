from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    # Arrange: No special setup needed for root redirect test

    # Act: Make a GET request to the root endpoint
    response = client.get("/")

    # Assert: Verify the response is a redirect to the static index page
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange: No special setup needed as activities are predefined

    # Act: Make a GET request to retrieve all activities
    response = client.get("/activities")

    # Assert: Verify the response contains the activities data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    # Arrange: Choose an activity and a new email not already signed up
    activity = "Programming Class"
    email = "test@mergington.edu"

    # Act: Make a POST request to sign up for the activity
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Verify successful signup and participant was added
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    # Verify the email was added to participants
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_activity_not_found():
    # Arrange: Use a non-existent activity name
    activity = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act: Attempt to sign up for the non-existent activity
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Verify 404 error for activity not found
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_already_signed_up():
    # Arrange: Sign up first, then try again
    activity = "Gym Class"
    email = "duplicate@mergington.edu"
    # First signup
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Attempt to sign up again
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert: Verify 400 error for already signed up
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_remove_participant_success():
    # Arrange: First sign up, then remove
    activity = "Basketball Team"
    email = "remove@mergington.edu"
    # Signup first
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act: Make a DELETE request to remove the participant
    response = client.delete(f"/activities/{activity}/remove", params={"email": email})

    # Assert: Verify successful removal
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    # Verify the email was removed from participants
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity]["participants"]


def test_remove_activity_not_found():
    # Arrange: Use a non-existent activity name
    activity = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act: Attempt to remove from non-existent activity
    response = client.delete(f"/activities/{activity}/remove", params={"email": email})

    # Assert: Verify 404 error for activity not found
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_not_signed_up():
    # Arrange: Try to remove without signing up first
    activity = "Tennis Club"
    email = "notsigned@mergington.edu"

    # Act: Attempt to remove participant who is not signed up
    response = client.delete(f"/activities/{activity}/remove", params={"email": email})

    # Assert: Verify 400 error for not signed up
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up"}