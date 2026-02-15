"""Tests for the FastAPI application."""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify we have all expected activities
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data
        assert "Art Studio" in data
        assert "Debate Team" in data
        assert "Robotics Club" in data
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_structure(self, client):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check Basketball activity structure
        basketball = activities["Basketball"]
        
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant."""
        email = "new_student@mergington.edu"
        
        response = client.post(
            f"/activities/Basketball/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        basketball = activities_response.json()["Basketball"]
        assert email in basketball["participants"]

    def test_signup_already_registered(self, client):
        """Test that duplicate signup is prevented."""
        email = "james@mergington.edu"  # Already registered for Basketball
        
        response = client.post(
            f"/activities/Basketball/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity."""
        response = client.post(
            f"/activities/Nonexistent/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_participants(self, client, reset_activities):
        """Test signing up multiple participants."""
        activity = "Tennis Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        tennis = activities_response.json()[activity]
        
        for email in emails:
            assert email in tennis["participants"]


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant."""
        email = "james@mergington.edu"  # Already registered for Basketball
        
        response = client.delete(
            f"/activities/Basketball/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        basketball = activities_response.json()["Basketball"]
        assert email not in basketball["participants"]

    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering someone not in the activity."""
        email = "not_registered@mergington.edu"
        
        response = client.delete(
            f"/activities/Basketball/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity."""
        response = client.delete(
            f"/activities/Nonexistent/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_and_rejoin(self, client, reset_activities):
        """Test that a participant can rejoin after unregistering."""
        email = "student@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Sign up again
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200


class TestIntegration:
    """Integration tests for multiple operations."""

    def test_complete_signup_workflow(self, client, reset_activities):
        """Test a complete signup and unregister workflow."""
        email1 = "user1@mergington.edu"
        email2 = "user2@mergington.edu"
        activity = "Chess Club"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = len(response.json()[activity]["participants"])
        
        # Sign up first user
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        assert response.status_code == 200
        
        # Sign up second user
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email2}
        )
        assert response.status_code == 200
        
        # Verify both are registered
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == initial_participants + 2
        
        # Unregister first user
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email1}
        )
        assert response.status_code == 200
        
        # Verify only second user remains
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email1 not in participants
        assert email2 in participants
        assert len(participants) == initial_participants + 1
