"""
Pytest configuration and fixtures for FastAPI tests
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a sample student email"""
    return "testuser@mergington.edu"


@pytest.fixture
def known_activity():
    """Provide a known activity from the database"""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """Provide a non-existent activity name"""
    return "Underwater Basketball Club"