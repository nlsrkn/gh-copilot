"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Soccer Club": {
            "description": "Team soccer practice and friendly matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions and acting workshops",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced problem-solving and math competitions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and STEM projects",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
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
    })
    yield
    activities.clear()


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Soccer Club" in data
        assert "Basketball Team" in data

    def test_get_activities_contains_correct_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Soccer Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_shows_current_participants(self, client):
        """Test that participant list is correct"""
        response = client.get("/activities")
        data = response.json()
        soccer = data["Soccer Club"]
        
        assert "alex@mergington.edu" in soccer["participants"]
        assert len(soccer["participants"]) == 1


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that participant is actually added"""
        client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Soccer Club"]["participants"]
        
        assert "newstudent@mergington.edu" in participants

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/NonexistentClub/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered(self, client):
        """Test that a student can't sign up twice"""
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "alex@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self, client):
        """Test signing up multiple different students"""
        client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Soccer Club"]["participants"]
        
        assert len(participants) == 3
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, client):
        """Test unregistering a participant"""
        response = client.post(
            "/activities/Soccer%20Club/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that participant is actually removed"""
        client.post(
            "/activities/Soccer%20Club/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Soccer Club"]["participants"]
        
        assert "alex@mergington.edu" not in participants
        assert len(participants) == 0

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/NonexistentClub/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregistering a student who isn't signed up"""
        response = client.post(
            "/activities/Soccer%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that a student can sign up after unregistering"""
        client.post(
            "/activities/Soccer%20Club/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "alex@mergington.edu"}
        )
        
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert "alex@mergington.edu" in data["Soccer Club"]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_complete_workflow(self, client):
        """Test a complete workflow: signup, view, unregister"""
        # Sign up
        signup_response = client.post(
            "/activities/Art%20Club/signup",
            params={"email": "testuser@mergington.edu"}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert "testuser@mergington.edu" in data["Art Club"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            "/activities/Art%20Club/unregister",
            params={"email": "testuser@mergington.edu"}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert "testuser@mergington.edu" not in final_data["Art Club"]["participants"]

    def test_multiple_activities_independent(self, client):
        """Test that activities are independent"""
        # Sign up for multiple activities
        client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "testuser@mergington.edu"}
        )
        client.post(
            "/activities/Art%20Club/signup",
            params={"email": "testuser@mergington.edu"}
        )
        
        # Unregister from one activity
        client.post(
            "/activities/Soccer%20Club/unregister",
            params={"email": "testuser@mergington.edu"}
        )
        
        # Check that user is still in Art Club
        response = client.get("/activities")
        data = response.json()
        
        assert "testuser@mergington.edu" not in data["Soccer Club"]["participants"]
        assert "testuser@mergington.edu" in data["Art Club"]["participants"]
