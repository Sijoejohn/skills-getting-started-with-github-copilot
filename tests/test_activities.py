"""
Test suite for Mergington High School Activities API endpoints.

All tests follow the AAA (Arrange-Act-Assert) pattern for clarity and consistency.
"""

import pytest
from urllib.parse import quote


# Root Endpoint Tests

def test_root_redirects_to_static_index(test_client):
    """Test that GET / redirects to /static/index.html"""
    # Arrange
    expected_redirect_url = "/static/index.html"
    
    # Act
    response = test_client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_redirect_url


# Activities Listing Tests

def test_get_activities_returns_all_activities(test_client):
    """Test that GET /activities returns all 9 activities"""
    # Arrange
    expected_activity_count = 9
    
    # Act
    response = test_client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == expected_activity_count
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activities_returns_correct_structure(test_client):
    """Test that each activity has the correct structure and fields"""
    # Arrange
    expected_fields = ["description", "schedule", "max_participants", "participants"]
    
    # Act
    response = test_client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    chess_club = data["Chess Club"]
    
    for field in expected_fields:
        assert field in chess_club
    
    assert isinstance(chess_club["participants"], list)
    assert isinstance(chess_club["max_participants"], int)


def test_get_activities_has_initial_participants(test_client):
    """Test that activities start with 2 initial participants each"""
    # Arrange
    expected_participant_count = 2
    
    # Act
    response = test_client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    chess_club = data["Chess Club"]
    
    assert len(chess_club["participants"]) == expected_participant_count
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


# Signup Endpoint Tests

def test_signup_successfully_adds_participant(test_client):
    """Test that a new student can successfully sign up for an activity"""
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    
    # Act
    response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(new_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    
    # Verify participant was actually added
    activities_response = test_client.get("/activities")
    activities_data = activities_response.json()
    assert new_email in activities_data[activity_name]["participants"]


def test_signup_with_nonexistent_activity_returns_404(test_client):
    """Test that signing up for a non-existent activity returns 404"""
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"
    
    # Act
    response = test_client.post(
        f"/activities/{quote(invalid_activity)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_with_duplicate_email_returns_400(test_client):
    """Test that signing up twice with the same email returns 400"""
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    
    # First signup (should succeed)
    first_response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert first_response.status_code == 200
    
    # Act - Second signup with same email (should fail)
    response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_with_spaces_in_activity_name(test_client):
    """Test that activity names with spaces are handled correctly"""
    # Arrange
    activity_name = "Programming Class"  # Has space
    email = "coder@mergington.edu"
    
    # Act
    response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_already_registered_participant_returns_400(test_client):
    """Test that signing up with an already registered email returns 400"""
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # Already in Chess Club
    
    # Act
    response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(existing_email)}"
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# Unregister Endpoint Tests

def test_unregister_successfully_removes_participant(test_client):
    """Test that unregistering removes a participant from an activity"""
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # Already registered
    
    # Verify participant exists before deletion
    activities_response = test_client.get("/activities")
    activities_data = activities_response.json()
    assert existing_email in activities_data[activity_name]["participants"]
    
    # Act
    response = test_client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(existing_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {existing_email} from {activity_name}"
    
    # Verify participant was actually removed
    activities_response = test_client.get("/activities")
    activities_data = activities_response.json()
    assert existing_email not in activities_data[activity_name]["participants"]


def test_unregister_from_nonexistent_activity_returns_404(test_client):
    """Test that unregistering from a non-existent activity returns 404"""
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "student@mergington.edu"
    
    # Act
    response = test_client.delete(
        f"/activities/{quote(invalid_activity)}/participants/{quote(email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_nonregistered_participant_returns_404(test_client):
    """Test that unregistering a non-registered participant returns 404"""
    # Arrange
    activity_name = "Chess Club"
    nonregistered_email = "notregistered@mergington.edu"
    
    # Act
    response = test_client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(nonregistered_email)}"
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"


def test_unregister_with_spaces_in_activity_name(test_client):
    """Test that unregistering from activities with spaces works correctly"""
    # Arrange
    activity_name = "Programming Class"  # Has space
    existing_email = "emma@mergington.edu"  # Already in Programming Class
    
    # Act
    response = test_client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(existing_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {existing_email} from {activity_name}"


def test_unregister_with_special_characters_in_email(test_client):
    """Test that emails with special characters are handled correctly"""
    # Arrange
    activity_name = "Chess Club"
    special_email = "test+special@mergington.edu"
    
    # First, sign up the participant
    signup_response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(special_email)}"
    )
    assert signup_response.status_code == 200
    
    # Act - Unregister with special character in email
    response = test_client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(special_email)}"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {special_email} from {activity_name}"


# Integration Tests

def test_full_signup_and_unregister_workflow(test_client):
    """Test the complete workflow of signing up and then unregistering"""
    # Arrange
    activity_name = "Drama Club"
    email = "workflow@mergington.edu"
    
    # Act & Assert - Sign up
    signup_response = test_client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200
    
    # Verify signup
    activities_response = test_client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]
    participant_count_after_signup = len(activities_data[activity_name]["participants"])
    
    # Act & Assert - Unregister
    unregister_response = test_client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )
    assert unregister_response.status_code == 200
    
    # Verify unregister
    activities_response = test_client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity_name]["participants"]
    participant_count_after_unregister = len(activities_data[activity_name]["participants"])
    assert participant_count_after_unregister == participant_count_after_signup - 1
