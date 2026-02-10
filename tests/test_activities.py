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
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Join our competitive soccer team for matches and practice",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Develop basketball skills and participate in friendly matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Explore acting, theater productions, and performance arts",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Express creativity through painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "charlotte@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "amelia@mergington.edu"]
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
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        
    def test_activity_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Soccer%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that signing up an already registered participant fails"""
        # First signup
        client.post("/activities/Soccer%20Team/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post("/activities/Soccer%20Team/signup?email=test@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_different_participants(self, client):
        """Test signing up multiple different participants"""
        participants = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in participants:
            response = client.post(f"/activities/Chess%20Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        chess_participants = activities_data["Chess Club"]["participants"]
        
        for email in participants:
            assert email in chess_participants


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # First, add a participant
        client.post("/activities/Drama%20Club/signup?email=testuser@mergington.edu")
        
        # Then unregister them
        response = client.delete(
            "/activities/Drama%20Club/unregister?email=testuser@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "testuser@mergington.edu" not in activities_data["Drama Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant that is not registered"""
        response = client.delete(
            "/activities/Art%20Studio/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_original_participant(self, client):
        """Test unregistering one of the original participants"""
        # Unregister an existing participant
        response = client.delete(
            "/activities/Soccer%20Team/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify they were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "james@mergington.edu" not in activities_data["Soccer Team"]["participants"]
        # But the other participant should still be there
        assert "sarah@mergington.edu" in activities_data["Soccer Team"]["participants"]


class TestIntegrationWorkflow:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Basketball Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        after_unregister = client.get("/activities")
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
        assert email not in after_unregister.json()[activity]["participants"]
    
    def test_multiple_activities_same_student(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitasker@mergington.edu"
        activities_to_join = ["Soccer Team", "Drama Club", "Science Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
