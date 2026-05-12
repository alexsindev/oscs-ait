"""
Comprehensive tests for the /api/v1/users endpoints.

This module tests:
- Role-based access control for all user endpoints
- User listing with proper permissions
- User retrieval (me, by ID) with proper permissions
- User update with proper permissions
- User deletion with proper permissions
- Student profile CRUD operations with proper permissions
- Business logic as specified in README.md
"""

import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import cleanup_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def _auto_clean() -> Generator[None]:
    """Automatically clean database before and after each test."""
    cleanup_database(client)
    yield
    cleanup_database(client)


def _unique_email(prefix: str = "user") -> str:
    """Generate a unique email for testing."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@mail.com"


def _register_and_login(
    role: str = "student",
    first_name: str = "Test",
    last_name: str = "User",
) -> tuple[dict[str, Any], str]:
    """Helper to register a user and return (user_data, token)."""
    email = _unique_email(role)
    password = f"{role}pass123"
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role": role,
    }
    register_resp = client.post("/api/v1/auth/register", json=user_data)
    assert register_resp.status_code == 201, f"Failed to register: {register_resp.text}"
    user = register_resp.json()

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code == 200, f"Failed to login: {login_resp.text}"
    token = login_resp.json()["access_token"]

    return user, token


def _headers(token: str) -> dict[str, str]:
    """Helper to create authorization headers."""
    return {"Authorization": f"Bearer {token}"}


# ===========================
# List All Users Tests (GET /users/)
# ===========================


class TestListUsers:
    """Tests for GET /users/ endpoint - Admin and Teacher can list all users."""

    def test_admin_can_list_all_users(self) -> None:
        """Test that admin can list all users."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        response = client.get("/api/v1/users/", headers=_headers(admin_token))

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2
        user_ids = [u["id"] for u in users]
        assert admin["id"] in user_ids
        assert student["id"] in user_ids

    def test_teacher_can_list_all_users(self) -> None:
        """Test that teacher can list all users."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        response = client.get("/api/v1/users/", headers=_headers(teacher_token))

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2

    def test_instructor_cannot_list_all_users(self) -> None:
        """Test that instructor cannot list all users."""
        instructor, instructor_token = _register_and_login("instructor")

        response = client.get("/api/v1/users/", headers=_headers(instructor_token))

        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_student_cannot_list_all_users(self) -> None:
        """Test that student cannot list all users."""
        student, student_token = _register_and_login("student")

        response = client.get("/api/v1/users/", headers=_headers(student_token))

        assert response.status_code == 403

    def test_guest_cannot_list_all_users(self) -> None:
        """Test that guest cannot list all users."""
        guest, guest_token = _register_and_login("guest")

        response = client.get("/api/v1/users/", headers=_headers(guest_token))

        assert response.status_code == 403

    def test_list_users_without_authentication(self) -> None:
        """Test that listing users without authentication fails."""
        response = client.get("/api/v1/users/")

        assert response.status_code == 401


# ===========================
# Read Current User Tests (GET /users/me)
# ===========================


class TestReadCurrentUser:
    """Tests for GET /users/me endpoint - All authenticated users can read their own details."""

    def test_admin_can_read_own_details(self) -> None:
        """Test that admin can read their own details."""
        admin, admin_token = _register_and_login("admin", "Admin", "User")

        response = client.get("/api/v1/users/me", headers=_headers(admin_token))

        assert response.status_code == 200
        user = response.json()
        assert user["id"] == admin["id"]
        assert user["first_name"] == "Admin"
        assert user["last_name"] == "User"
        assert user["role"] == "admin"
        assert "password" not in user
        assert "hashed_password" not in user

    def test_teacher_can_read_own_details(self) -> None:
        """Test that teacher can read their own details."""
        teacher, teacher_token = _register_and_login("teacher")

        response = client.get("/api/v1/users/me", headers=_headers(teacher_token))

        assert response.status_code == 200
        assert response.json()["role"] == "teacher"

    def test_instructor_can_read_own_details(self) -> None:
        """Test that instructor can read their own details."""
        instructor, instructor_token = _register_and_login("instructor")

        response = client.get("/api/v1/users/me", headers=_headers(instructor_token))

        assert response.status_code == 200
        assert response.json()["role"] == "instructor"

    def test_student_can_read_own_details(self) -> None:
        """Test that student can read their own details."""
        student, student_token = _register_and_login("student")

        response = client.get("/api/v1/users/me", headers=_headers(student_token))

        assert response.status_code == 200
        assert response.json()["role"] == "student"

    def test_guest_can_read_own_details(self) -> None:
        """Test that guest can read their own details."""
        guest, guest_token = _register_and_login("guest")

        response = client.get("/api/v1/users/me", headers=_headers(guest_token))

        assert response.status_code == 200
        assert response.json()["role"] == "guest"

    def test_me_includes_student_profile_if_exists(self) -> None:
        """Test that /users/me includes student profile if it exists."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create student profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test demographics",
            "matthayom_level": 3,
        }
        profile_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(student_token),
            json=profile_data,
        )
        assert profile_resp.status_code == 201

        # Get user details
        response = client.get("/api/v1/users/me", headers=_headers(student_token))

        assert response.status_code == 200
        user = response.json()
        assert user["student_profile"] is not None
        assert user["student_profile"]["demographics"] == "Test demographics"
        assert user["student_profile"]["matthayom_level"] == 3

    def test_me_without_authentication(self) -> None:
        """Test that accessing /users/me without authentication fails."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401


# ===========================
# Read User by ID Tests (GET /users/{id})
# ===========================


class TestReadUserById:
    """Tests for GET /users/{id} endpoint - Everyone except Guest can read others; Guest only self."""

    def test_admin_can_read_any_user(self) -> None:
        """Test that admin can read any user's details."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        response = client.get(f"/api/v1/users/{student['id']}", headers=_headers(admin_token))

        assert response.status_code == 200
        assert response.json()["id"] == student["id"]

    def test_teacher_can_read_any_user(self) -> None:
        """Test that teacher can read any user's details."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        response = client.get(f"/api/v1/users/{student['id']}", headers=_headers(teacher_token))

        assert response.status_code == 200
        assert response.json()["id"] == student["id"]

    def test_instructor_can_read_any_user(self) -> None:
        """Test that instructor can read any user's details."""
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        response = client.get(f"/api/v1/users/{student['id']}", headers=_headers(instructor_token))

        assert response.status_code == 200
        assert response.json()["id"] == student["id"]

    def test_student_can_read_any_user(self) -> None:
        """Test that student can read any user's details."""
        student1, student1_token = _register_and_login("student")
        student2, _ = _register_and_login("student", "Student", "Two")

        response = client.get(f"/api/v1/users/{student2['id']}", headers=_headers(student1_token))

        assert response.status_code == 200
        assert response.json()["id"] == student2["id"]

    def test_guest_can_only_read_own_details(self) -> None:
        """Test that guest can only read their own details."""
        guest, guest_token = _register_and_login("guest")
        student, _ = _register_and_login("student")

        # Guest can read their own details
        response_self = client.get(f"/api/v1/users/{guest['id']}", headers=_headers(guest_token))
        assert response_self.status_code == 200

        # Guest cannot read other users
        response_other = client.get(f"/api/v1/users/{student['id']}", headers=_headers(guest_token))
        assert response_other.status_code == 403
        assert "Guests can only view their own user details" in response_other.json()["detail"]

    def test_read_nonexistent_user(self) -> None:
        """Test that reading non-existent user returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(f"/api/v1/users/{uuid.uuid4()}", headers=_headers(admin_token))

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_user_by_id_includes_student_profile(self) -> None:
        """Test that GET /users/{id} includes student profile if exists."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create student profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test demographics",
            "matthayom_level": 5,
        }
        client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )

        # Get user by ID
        response = client.get(f"/api/v1/users/{student['id']}", headers=_headers(admin_token))

        assert response.status_code == 200
        user = response.json()
        assert user["student_profile"] is not None
        assert user["student_profile"]["matthayom_level"] == 5


# ===========================
# Update User Tests (PATCH /users/{id})
# ===========================


class TestUpdateUser:
    """Tests for PATCH /users/{id} endpoint - Admin can update anyone; others only themselves."""

    def test_admin_can_update_any_user(self) -> None:
        """Test that admin can update any user's information."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student", "Old", "Name")

        update_data = {
            "first_name": "New",
            "last_name": "Name",
        }
        response = client.patch(
            f"/api/v1/users/{student['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["first_name"] == "New"
        assert updated["last_name"] == "Name"
        assert updated["id"] == student["id"]

    def test_teacher_can_update_own_details(self) -> None:
        """Test that teacher can update their own details."""
        teacher, teacher_token = _register_and_login("teacher", "Old", "Teacher")

        update_data = {"first_name": "Updated"}
        response = client.patch(
            f"/api/v1/users/{teacher['id']}",
            headers=_headers(teacher_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"

    def test_teacher_cannot_update_other_users(self) -> None:
        """Test that teacher cannot update other users."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        update_data = {"first_name": "Hacked"}
        response = client.patch(
            f"/api/v1/users/{student['id']}",
            headers=_headers(teacher_token),
            json=update_data,
        )

        assert response.status_code == 403
        assert "Only admins can update other users" in response.json()["detail"]

    def test_student_can_update_own_details(self) -> None:
        """Test that student can update their own details."""
        student, student_token = _register_and_login("student")

        update_data = {
            "first_name": "Updated",
            "last_name": "Student",
            "email": _unique_email("newemail"),
        }
        response = client.patch(
            f"/api/v1/users/{student['id']}",
            headers=_headers(student_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["first_name"] == "Updated"
        assert updated["last_name"] == "Student"

    def test_student_cannot_update_other_users(self) -> None:
        """Test that student cannot update other users."""
        student1, student1_token = _register_and_login("student")
        student2, _ = _register_and_login("student", "Other", "Student")

        update_data = {"first_name": "Hacked"}
        response = client.patch(
            f"/api/v1/users/{student2['id']}",
            headers=_headers(student1_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_guest_can_update_own_details(self) -> None:
        """Test that guest can update their own details."""
        guest, guest_token = _register_and_login("guest")

        update_data = {"first_name": "Updated"}
        response = client.patch(
            f"/api/v1/users/{guest['id']}",
            headers=_headers(guest_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"

    def test_update_user_partial_fields(self) -> None:
        """Test that updating user with partial fields works."""
        admin, admin_token = _register_and_login("admin", "First", "Last")

        # Update only first name
        response = client.patch(
            f"/api/v1/users/{admin['id']}",
            headers=_headers(admin_token),
            json={"first_name": "NewFirst"},
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["first_name"] == "NewFirst"
        assert updated["last_name"] == "Last"  # Unchanged

    def test_update_nonexistent_user(self) -> None:
        """Test that updating non-existent user returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.patch(
            f"/api/v1/users/{uuid.uuid4()}",
            headers=_headers(admin_token),
            json={"first_name": "Test"},
        )

        assert response.status_code == 404


# ===========================
# Delete User Tests (DELETE /users/{id})
# ===========================


class TestDeleteUser:
    """Tests for DELETE /users/{id} endpoint - Only admin can delete users."""

    def test_admin_can_delete_any_user(self) -> None:
        """Test that admin can delete any user."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        response = client.delete(f"/api/v1/users/{student['id']}", headers=_headers(admin_token))

        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(f"/api/v1/users/{student['id']}", headers=_headers(admin_token))
        assert get_response.status_code == 404

    def test_teacher_cannot_delete_users(self) -> None:
        """Test that teacher cannot delete users."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        response = client.delete(f"/api/v1/users/{student['id']}", headers=_headers(teacher_token))

        assert response.status_code == 403
        assert "Only admins can delete users" in response.json()["detail"]

    def test_instructor_cannot_delete_users(self) -> None:
        """Test that instructor cannot delete users."""
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        response = client.delete(f"/api/v1/users/{student['id']}", headers=_headers(instructor_token))

        assert response.status_code == 403

    def test_student_cannot_delete_users(self) -> None:
        """Test that student cannot delete users."""
        student1, student1_token = _register_and_login("student")
        student2, _ = _register_and_login("student", "Other", "Student")

        response = client.delete(f"/api/v1/users/{student2['id']}", headers=_headers(student1_token))

        assert response.status_code == 403

    def test_student_cannot_delete_self(self) -> None:
        """Test that student cannot even delete themselves."""
        student, student_token = _register_and_login("student")

        response = client.delete(f"/api/v1/users/{student['id']}", headers=_headers(student_token))

        assert response.status_code == 403

    def test_guest_cannot_delete_users(self) -> None:
        """Test that guest cannot delete users."""
        guest, guest_token = _register_and_login("guest")

        response = client.delete(f"/api/v1/users/{guest['id']}", headers=_headers(guest_token))

        assert response.status_code == 403

    def test_delete_nonexistent_user(self) -> None:
        """Test that deleting non-existent user returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.delete(f"/api/v1/users/{uuid.uuid4()}", headers=_headers(admin_token))

        assert response.status_code == 404


# ===========================
# List All Student Profiles Tests (GET /users/student_profiles)
# ===========================


class TestListStudentProfiles:
    """Tests for GET /users/student_profiles endpoint - Admin and Teacher only."""

    def test_admin_can_list_all_student_profiles(self) -> None:
        """Test that admin can list all student profiles."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create a profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )

        response = client.get("/api/v1/users/student_profiles", headers=_headers(admin_token))

        assert response.status_code == 200
        profiles = response.json()
        assert isinstance(profiles, list)
        assert len(profiles) >= 1

    def test_teacher_can_list_all_student_profiles(self) -> None:
        """Test that teacher can list all student profiles."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create a profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 2,
        }
        client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(teacher_token),
            json=profile_data,
        )

        response = client.get("/api/v1/users/student_profiles", headers=_headers(teacher_token))

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_instructor_cannot_list_student_profiles(self) -> None:
        """Test that instructor cannot list student profiles."""
        instructor, instructor_token = _register_and_login("instructor")

        response = client.get("/api/v1/users/student_profiles", headers=_headers(instructor_token))

        assert response.status_code == 403

    def test_student_cannot_list_all_student_profiles(self) -> None:
        """Test that student cannot list all student profiles."""
        student, student_token = _register_and_login("student")

        response = client.get("/api/v1/users/student_profiles", headers=_headers(student_token))

        assert response.status_code == 403

    def test_guest_cannot_list_student_profiles(self) -> None:
        """Test that guest cannot list student profiles."""
        guest, guest_token = _register_and_login("guest")

        response = client.get("/api/v1/users/student_profiles", headers=_headers(guest_token))

        assert response.status_code == 403


# ===========================
# Create Student Profile Tests (POST /users/student_profiles)
# ===========================


class TestCreateStudentProfile:
    """Tests for POST /users/student_profiles endpoint - Admin, Teacher, and own Student."""

    def test_admin_can_create_student_profile(self) -> None:
        """Test that admin can create student profile for any user."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        profile_data = {
            "user_id": student["id"],
            "demographics": "Test demographics",
            "matthayom_level": 4,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )

        assert response.status_code == 201
        profile = response.json()
        assert profile["user_id"] == student["id"]
        assert profile["demographics"] == "Test demographics"
        assert profile["matthayom_level"] == 4
        assert "id" in profile

    def test_teacher_can_create_student_profile(self) -> None:
        """Test that teacher can create student profile."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        profile_data = {
            "user_id": student["id"],
            "demographics": "Created by teacher",
            "matthayom_level": 1,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(teacher_token),
            json=profile_data,
        )

        assert response.status_code == 201
        assert response.json()["demographics"] == "Created by teacher"

    def test_student_can_create_own_profile(self) -> None:
        """Test that student can create their own profile."""
        student, student_token = _register_and_login("student")

        profile_data = {
            "user_id": student["id"],
            "demographics": "My profile",
            "matthayom_level": 6,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(student_token),
            json=profile_data,
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == student["id"]

    def test_student_cannot_create_profile_for_others(self) -> None:
        """Test that student cannot create profile for other users."""
        student1, student1_token = _register_and_login("student")
        student2, _ = _register_and_login("student", "Other", "Student")

        profile_data = {
            "user_id": student2["id"],
            "demographics": "Trying to hack",
            "matthayom_level": 3,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(student1_token),
            json=profile_data,
        )

        assert response.status_code == 403
        assert "Students can only create their own student profiles" in response.json()["detail"]

    def test_instructor_cannot_create_student_profile(self) -> None:
        """Test that instructor cannot create student profiles."""
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 2,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(instructor_token),
            json=profile_data,
        )

        assert response.status_code == 403

    def test_guest_cannot_create_student_profile(self) -> None:
        """Test that guest cannot create student profiles."""
        guest, guest_token = _register_and_login("guest")

        profile_data = {
            "user_id": guest["id"],
            "demographics": "Test",
            "matthayom_level": 1,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(guest_token),
            json=profile_data,
        )

        assert response.status_code == 403

    def test_create_duplicate_student_profile(self) -> None:
        """Test that creating duplicate profile for same user fails."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        profile_data = {
            "user_id": student["id"],
            "demographics": "First",
            "matthayom_level": 3,
        }
        # First creation
        response1 = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        assert response1.status_code == 201

        # Second creation should fail
        response2 = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        assert response2.status_code == 400
        assert "Student profile already exists" in response2.json()["detail"]

    def test_create_profile_for_nonexistent_user(self) -> None:
        """Test that creating profile for non-existent user fails."""
        admin, admin_token = _register_and_login("admin")

        profile_data = {
            "user_id": str(uuid.uuid4()),
            "demographics": "Test",
            "matthayom_level": 3,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_create_profile_with_invalid_matthayom_level(self) -> None:
        """Test that creating profile with invalid matthayom_level fails."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        # Test level < 1
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 0,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        assert response.status_code == 422

        # Test level > 6
        profile_data["matthayom_level"] = 7
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        assert response.status_code == 422

    def test_create_profile_with_optional_demographics(self) -> None:
        """Test that demographics field is optional."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        profile_data = {
            "user_id": student["id"],
            "matthayom_level": 3,
        }
        response = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )

        assert response.status_code == 201
        profile = response.json()
        assert profile["demographics"] is None


# ===========================
# Read Student Profile by ID Tests (GET /users/student_profiles/{id})
# ===========================


class TestReadStudentProfileById:
    """Tests for GET /users/student_profiles/{id} endpoint."""

    def test_admin_can_read_any_student_profile(self) -> None:
        """Test that admin can read any student profile."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 4,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Read profile
        response = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json()["id"] == profile_id

    def test_teacher_can_read_any_student_profile(self) -> None:
        """Test that teacher can read any student profile."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 2,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(teacher_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Read profile
        response = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 200

    def test_student_can_read_own_profile(self) -> None:
        """Test that student can read their own profile."""
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "My profile",
            "matthayom_level": 5,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(student_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Read profile
        response = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == student["id"]

    def test_student_cannot_read_other_profiles(self) -> None:
        """Test that student cannot read other students' profiles."""
        admin, admin_token = _register_and_login("admin")
        student1, student1_token = _register_and_login("student")
        student2, student2_token = _register_and_login("student", "Other", "Student")

        # Create profile for student2
        profile_data = {
            "user_id": student2["id"],
            "demographics": "Other student",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Student1 tries to read student2's profile
        response = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(student1_token),
        )

        assert response.status_code == 403
        assert "Students can only view their own student profiles" in response.json()["detail"]

    def test_instructor_cannot_read_student_profiles(self) -> None:
        """Test that instructor cannot read student profiles."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Instructor tries to read
        response = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403

    def test_guest_cannot_read_student_profiles(self) -> None:
        """Test that guest cannot read student profiles."""
        admin, admin_token = _register_and_login("admin")
        guest, guest_token = _register_and_login("guest")
        student, _ = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Guest tries to read
        response = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403

    def test_read_nonexistent_student_profile(self) -> None:
        """Test that reading non-existent profile returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/users/student_profiles/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404


# ===========================
# Update Student Profile Tests (PATCH /users/student_profiles/{id})
# ===========================


class TestUpdateStudentProfile:
    """Tests for PATCH /users/student_profiles/{id} endpoint."""

    def test_admin_can_update_any_student_profile(self) -> None:
        """Test that admin can update any student profile."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Original",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Update profile
        update_data = {
            "demographics": "Updated by admin",
            "matthayom_level": 5,
        }
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["demographics"] == "Updated by admin"
        assert updated["matthayom_level"] == 5

    def test_teacher_can_update_any_student_profile(self) -> None:
        """Test that teacher can update any student profile."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Original",
            "matthayom_level": 2,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(teacher_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Update profile
        update_data = {"matthayom_level": 4}
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(teacher_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["matthayom_level"] == 4

    def test_student_can_update_own_profile(self) -> None:
        """Test that student can update their own profile."""
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Original",
            "matthayom_level": 1,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(student_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Update profile
        update_data = {
            "demographics": "Updated by self",
            "matthayom_level": 6,
        }
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(student_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["demographics"] == "Updated by self"

    def test_student_cannot_update_other_profiles(self) -> None:
        """Test that student cannot update other students' profiles."""
        admin, admin_token = _register_and_login("admin")
        student1, student1_token = _register_and_login("student")
        student2, student2_token = _register_and_login("student", "Other", "Student")

        # Create profile for student2
        profile_data = {
            "user_id": student2["id"],
            "demographics": "Other",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Student1 tries to update student2's profile
        update_data = {"demographics": "Hacked"}
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(student1_token),
            json=update_data,
        )

        assert response.status_code == 403
        assert "Students can only update their own student profiles" in response.json()["detail"]

    def test_instructor_cannot_update_student_profiles(self) -> None:
        """Test that instructor cannot update student profiles."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Instructor tries to update
        update_data = {"matthayom_level": 5}
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(instructor_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_guest_cannot_update_student_profiles(self) -> None:
        """Test that guest cannot update student profiles."""
        admin, admin_token = _register_and_login("admin")
        guest, guest_token = _register_and_login("guest")
        student, _ = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Guest tries to update
        update_data = {"matthayom_level": 5}
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(guest_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_update_profile_partial_fields(self) -> None:
        """Test that updating profile with partial fields works."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Original",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Update only demographics
        update_data = {"demographics": "Updated"}
        response = client.patch(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["demographics"] == "Updated"
        assert updated["matthayom_level"] == 3  # Unchanged

    def test_update_nonexistent_student_profile(self) -> None:
        """Test that updating non-existent profile returns 404."""
        admin, admin_token = _register_and_login("admin")

        update_data = {"matthayom_level": 5}
        response = client.patch(
            f"/api/v1/users/student_profiles/{uuid.uuid4()}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 404


# ===========================
# Delete Student Profile Tests (DELETE /users/student_profiles/{id})
# ===========================


class TestDeleteStudentProfile:
    """Tests for DELETE /users/student_profiles/{id} endpoint - Only admin can delete."""

    def test_admin_can_delete_student_profile(self) -> None:
        """Test that admin can delete any student profile."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Delete profile
        response = client.delete(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 204

        # Verify deletion
        get_resp = client.get(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(admin_token),
        )
        assert get_resp.status_code == 404

    def test_teacher_cannot_delete_student_profile(self) -> None:
        """Test that teacher cannot delete student profiles."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(admin_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Teacher tries to delete
        response = client.delete(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 403
        assert "Only admins can delete student profiles" in response.json()["detail"]

    def test_student_cannot_delete_own_profile(self) -> None:
        """Test that student cannot delete their own profile."""
        student, student_token = _register_and_login("student")

        # Create profile
        profile_data = {
            "user_id": student["id"],
            "demographics": "Test",
            "matthayom_level": 3,
        }
        create_resp = client.post(
            "/api/v1/users/student_profiles",
            headers=_headers(student_token),
            json=profile_data,
        )
        profile_id = create_resp.json()["id"]

        # Student tries to delete own profile
        response = client.delete(
            f"/api/v1/users/student_profiles/{profile_id}",
            headers=_headers(student_token),
        )

        assert response.status_code == 403

    def test_delete_nonexistent_student_profile(self) -> None:
        """Test that deleting non-existent profile returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.delete(
            f"/api/v1/users/student_profiles/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
