import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


class TestActivitiesAPI:
    """Test cases for the Activities API"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200

        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

        # Check that each activity has the expected structure
        for name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_with_existing_participants(self, client):
        """Test that activities with existing participants are returned correctly"""
        response = client.get("/activities")
        activities = response.json()

        # Check Chess Club has participants
        chess_club = activities.get("Chess Club")
        assert chess_club is not None
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        activity_name = "Basketball Team"
        email = "test@mergington.edu"

        # Get initial participants count
        response = client.get("/activities")
        initial_activities = response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in the initial data

        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "Student already signed up" in result["detail"]

    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already in the initial data

        # Get initial participants count
        response = client.get("/activities")
        initial_activities = response.json()
        initial_count = len(initial_activities[activity_name]["participants"])

        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/unregister",
            params={"email": "test@mergington.edu"}
        )

        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        activity_name = "Basketball Team"
        email = "notregistered@mergington.edu"

        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "Student is not signed up" in result["detail"]

    def test_root_redirect(self, client):
        """Test root endpoint redirects to static index"""
        response = client.get("/")
        assert response.status_code == 200  # FastAPI TestClient follows redirects by default
        # The response should contain the HTML content
        assert "Mergington High School" in response.text
