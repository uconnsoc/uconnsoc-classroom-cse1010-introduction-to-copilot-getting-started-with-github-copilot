"""
Integration tests for signup and unregister flows
"""
import pytest


class TestSignupFlow:
    """Tests for POST /activities/{activity_name}/signup"""

    def test_signup_successful(self, client, known_activity, sample_email):
        """Successful signup should return 200 and confirmation message"""
        response = client.post(
            f"/activities/{known_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

    def test_signup_nonexistent_activity_returns_404(self, client, nonexistent_activity):
        """Signup for non-existent activity should return 404"""
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_returns_400(self, client, known_activity):
        """Signing up twice should return 400"""
        email = "duplicate@mergington.edu"
        # First signup
        client.post(f"/activities/{known_activity}/signup", params={"email": email})
        # Second signup (should fail)
        response = client.post(
            f"/activities/{known_activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestUnregisterFlow:
    """Tests for DELETE /activities/{activity_name}/signup"""

    def test_unregister_successful(self, client, known_activity, sample_email):
        """Unregister from an activity should work"""
        # First signup
        client.post(f"/activities/{known_activity}/signup", params={"email": sample_email})
        # Then unregister
        response = client.delete(
            f"/activities/{known_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_not_signed_up_returns_400(self, client, known_activity):
        """Unregistering from activity user isn't in should return 400"""
        response = client.delete(
            f"/activities/{known_activity}/signup",
            params={"email": "neverjoined@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()