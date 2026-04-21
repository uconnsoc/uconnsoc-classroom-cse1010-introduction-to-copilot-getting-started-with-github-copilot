"""
Pytest configuration and fixtures for the Mergington High School Activities API tests.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import create_app


# Test data - a fresh copy of activities for each test
TEST_ACTIVITIES = {
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
    }
}


@pytest.fixture
def test_activities():
    """Provide a fresh copy of test activities for each test."""
    return copy.deepcopy(TEST_ACTIVITIES)


@pytest.fixture
def client(test_activities):
    """Provide a TestClient with test activities data."""
    app = create_app(activities=test_activities)
    return TestClient(app)
