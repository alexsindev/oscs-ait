"""
Comprehensive tests for the /api/v1/enrollments endpoints.

This module tests:
- Enrollment listing with proper role-based permissions
- Enrollment creation with proper permissions and validation
- Enrollment retrieval by ID with proper permissions
- Enrollment update (status) with proper permissions
- Enrollment deletion with proper permissions
- Listing enrollments by user ID with proper permissions
- Listing enrollments by course ID with proper permissions
- Business logic validation (duplicate enrollments, non-existent users/courses)
- All permissions as specified in README.md
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


def _create_course_group(token: str, name: str = "Test Group") -> dict[str, Any]:
    """Helper to create a course group."""
    group_data = {"name": name, "description": "Test description"}
    response = client.post(
        "/api/v1/courses/groups",
        headers=_headers(token),
        json=group_data,
    )
    assert response.status_code == 201, f"Failed to create course group: {response.text}"
    return response.json()


def _create_course(
    token: str,
    teacher_id: str,
    course_group_id: str,
    name: str = "Test Course",
) -> dict[str, Any]:
    """Helper to create a course."""
    course_data = {
        "name": name,
        "description": "Test course description",
        "teacher_id": teacher_id,
        "course_group_id": course_group_id,
    }
    response = client.post(
        "/api/v1/courses/",
        headers=_headers(token),
        json=course_data,
    )
    assert response.status_code == 201, f"Failed to create course: {response.text}"
    return response.json()


def _create_enrollment(
    token: str,
    user_id: str,
    course_id: str,
) -> dict[str, Any]:
    """Helper to create an enrollment."""
    enrollment_data = {
        "user_id": user_id,
        "course_id": course_id,
    }
    response = client.post(
        "/api/v1/enrollments/",
        headers=_headers(token),
        json=enrollment_data,
    )
    assert response.status_code == 201, f"Failed to create enrollment: {response.text}"
    return response.json()


# ===========================
# List All Enrollments Tests (GET /enrollments/)
# ===========================


class TestListEnrollments:
    """Tests for GET /enrollments/ endpoint - Admin and Teacher only."""

    def test_admin_can_list_all_enrollments(self) -> None:
        """Test that admin can list all enrollments."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test Group")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get("/api/v1/enrollments/", headers=_headers(admin_token))

        assert response.status_code == 200
        enrollments = response.json()
        assert isinstance(enrollments, list)
        assert len(enrollments) >= 1

    def test_teacher_can_list_all_enrollments(self) -> None:
        """Test that teacher can list all enrollments."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(teacher_token, "Test Group")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Science")
        _create_enrollment(teacher_token, student["id"], course["id"])

        response = client.get("/api/v1/enrollments/", headers=_headers(teacher_token))

        assert response.status_code == 200
        enrollments = response.json()
        assert isinstance(enrollments, list)
        assert len(enrollments) >= 1

    def test_instructor_cannot_list_all_enrollments(self) -> None:
        """Test that instructor cannot list all enrollments."""
        instructor, instructor_token = _register_and_login("instructor")

        response = client.get("/api/v1/enrollments/", headers=_headers(instructor_token))

        assert response.status_code == 403
        assert "Only admins and teachers" in response.json()["detail"]

    def test_student_cannot_list_all_enrollments(self) -> None:
        """Test that student cannot list all enrollments."""
        student, student_token = _register_and_login("student")

        response = client.get("/api/v1/enrollments/", headers=_headers(student_token))

        assert response.status_code == 403

    def test_guest_cannot_list_all_enrollments(self) -> None:
        """Test that guest cannot list all enrollments."""
        guest, guest_token = _register_and_login("guest")

        response = client.get("/api/v1/enrollments/", headers=_headers(guest_token))

        assert response.status_code == 403

    def test_list_enrollments_without_authentication(self) -> None:
        """Test that listing enrollments without authentication fails."""
        response = client.get("/api/v1/enrollments/")

        assert response.status_code == 401


# ===========================
# Create Enrollment Tests (POST /enrollments/)
# ===========================


class TestCreateEnrollment:
    """Tests for POST /enrollments/ endpoint - Admin, Teacher, and Students (own only)."""

    def test_admin_can_create_enrollment_for_any_student(self) -> None:
        """Test that admin can create enrollment for any student."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course
        group = _create_course_group(admin_token, "Academics")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")

        # Create enrollment
        enrollment_data = {
            "user_id": student["id"],
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(admin_token),
            json=enrollment_data,
        )

        assert response.status_code == 201
        enrollment = response.json()
        assert enrollment["user_id"] == student["id"]
        assert enrollment["course_id"] == course["id"]
        assert enrollment["status"] == "active"
        assert "id" in enrollment

    def test_teacher_can_create_enrollment_for_any_student(self) -> None:
        """Test that teacher can create enrollment for any student."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course
        group = _create_course_group(teacher_token, "Science")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Biology")

        # Create enrollment
        enrollment_data = {
            "user_id": student["id"],
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(teacher_token),
            json=enrollment_data,
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == student["id"]

    def test_student_can_create_enrollment_for_self(self) -> None:
        """Test that student can enroll themselves in courses."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create course
        group = _create_course_group(admin_token, "Arts")
        course = _create_course(admin_token, teacher["id"], group["id"], "Painting")

        # Student enrolls themselves
        enrollment_data = {
            "user_id": student["id"],
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(student_token),
            json=enrollment_data,
        )

        assert response.status_code == 201
        enrollment = response.json()
        assert enrollment["user_id"] == student["id"]
        assert enrollment["status"] == "active"

    def test_student_cannot_create_enrollment_for_others(self) -> None:
        """Test that student cannot enroll other students."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, _ = _register_and_login("student", "Student", "Two")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Test Course")

        # Student1 tries to enroll Student2
        enrollment_data = {
            "user_id": student2["id"],
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(student1_token),
            json=enrollment_data,
        )

        assert response.status_code == 403
        assert "Students can only create enrollments for themselves" in response.json()["detail"]

    def test_instructor_cannot_create_enrollment(self) -> None:
        """Test that instructor cannot create enrollments."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Test Course")

        # Instructor tries to create enrollment
        enrollment_data = {
            "user_id": student["id"],
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(instructor_token),
            json=enrollment_data,
        )

        assert response.status_code == 403
        assert "Only admins, teachers, and students can create enrollments" in response.json()["detail"]

    def test_guest_cannot_create_enrollment(self) -> None:
        """Test that guest cannot create enrollments."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        guest, guest_token = _register_and_login("guest")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Test Course")

        # Guest tries to create enrollment
        enrollment_data = {
            "user_id": guest["id"],
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(guest_token),
            json=enrollment_data,
        )

        assert response.status_code == 403

    def test_create_duplicate_enrollment(self) -> None:
        """Test that creating duplicate enrollment for same user/course fails."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")

        # Create first enrollment
        enrollment_data = {
            "user_id": student["id"],
            "course_id": course["id"],
        }
        response1 = client.post(
            "/api/v1/enrollments/",
            headers=_headers(admin_token),
            json=enrollment_data,
        )
        assert response1.status_code == 201

        # Try to create duplicate enrollment
        response2 = client.post(
            "/api/v1/enrollments/",
            headers=_headers(admin_token),
            json=enrollment_data,
        )
        assert response2.status_code == 400
        assert "Enrollment already exists" in response2.json()["detail"]

    def test_create_enrollment_with_nonexistent_user(self) -> None:
        """Test that creating enrollment with non-existent user fails."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")

        # Try to create enrollment with fake user
        enrollment_data = {
            "user_id": str(uuid.uuid4()),
            "course_id": course["id"],
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(admin_token),
            json=enrollment_data,
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_create_enrollment_with_nonexistent_course(self) -> None:
        """Test that creating enrollment with non-existent course fails."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        # Try to create enrollment with fake course
        enrollment_data = {
            "user_id": student["id"],
            "course_id": str(uuid.uuid4()),
        }
        response = client.post(
            "/api/v1/enrollments/",
            headers=_headers(admin_token),
            json=enrollment_data,
        )

        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]

    def test_create_enrollment_without_authentication(self) -> None:
        """Test that creating enrollment without authentication fails."""
        enrollment_data = {
            "user_id": str(uuid.uuid4()),
            "course_id": str(uuid.uuid4()),
        }
        response = client.post("/api/v1/enrollments/", json=enrollment_data)

        assert response.status_code == 401


# ===========================
# Get Enrollment by ID Tests (GET /enrollments/{id})
# ===========================


class TestGetEnrollment:
    """Tests for GET /enrollments/{id} endpoint - All except Guest can read."""

    def test_admin_can_get_enrollment(self) -> None:
        """Test that admin can get enrollment details."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == enrollment["id"]
        assert retrieved["user_id"] == student["id"]
        assert retrieved["course_id"] == course["id"]
        assert retrieved["status"] == "active"
        # Verify relationships are included
        assert "user" in retrieved
        assert "course" in retrieved

    def test_teacher_can_get_enrollment(self) -> None:
        """Test that teacher can get enrollment details."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Science")
        enrollment = _create_enrollment(teacher_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 200
        assert response.json()["id"] == enrollment["id"]

    def test_instructor_can_get_enrollment(self) -> None:
        """Test that instructor can get enrollment details."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 200
        assert response.json()["id"] == enrollment["id"]

    def test_student_can_get_enrollment(self) -> None:
        """Test that student can get enrollment details."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        assert response.json()["id"] == enrollment["id"]

    def test_guest_cannot_get_enrollment(self) -> None:
        """Test that guest cannot get enrollment details."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")
        guest, guest_token = _register_and_login("guest")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403
        assert "Guests cannot view enrollments" in response.json()["detail"]

    def test_get_nonexistent_enrollment(self) -> None:
        """Test that getting non-existent enrollment returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/enrollments/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Enrollment not found" in response.json()["detail"]

    def test_get_enrollment_without_authentication(self) -> None:
        """Test that getting enrollment without authentication fails."""
        response = client.get(f"/api/v1/enrollments/{uuid.uuid4()}")

        assert response.status_code == 401


# ===========================
# Update Enrollment Tests (PATCH /enrollments/{id})
# ===========================


class TestUpdateEnrollment:
    """Tests for PATCH /enrollments/{id} endpoint - Admin and Teacher only."""

    def test_admin_can_update_enrollment_status(self) -> None:
        """Test that admin can update enrollment status."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Update status to completed
        update_data = {"status": "completed"}
        response = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["status"] == "completed"
        assert updated["id"] == enrollment["id"]

    def test_teacher_can_update_enrollment_status(self) -> None:
        """Test that teacher can update enrollment status."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Science")
        enrollment = _create_enrollment(teacher_token, student["id"], course["id"])

        # Update status to dropped
        update_data = {"status": "dropped"}
        response = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(teacher_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "dropped"

    def test_update_enrollment_all_statuses(self) -> None:
        """Test that all valid enrollment statuses can be set."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Test all valid statuses
        for status in ["active", "completed", "dropped"]:
            update_data = {"status": status}
            response = client.patch(
                f"/api/v1/enrollments/{enrollment['id']}",
                headers=_headers(admin_token),
                json=update_data,
            )
            assert response.status_code == 200
            assert response.json()["status"] == status

    def test_instructor_cannot_update_enrollment(self) -> None:
        """Test that instructor cannot update enrollment status."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Instructor tries to update
        update_data = {"status": "completed"}
        response = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(instructor_token),
            json=update_data,
        )

        assert response.status_code == 403
        assert "Only admins and teachers can update enrollments" in response.json()["detail"]

    def test_student_cannot_update_enrollment(self) -> None:
        """Test that student cannot update enrollment status."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Student tries to update their own enrollment
        update_data = {"status": "completed"}
        response = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(student_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_guest_cannot_update_enrollment(self) -> None:
        """Test that guest cannot update enrollment status."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")
        guest, guest_token = _register_and_login("guest")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Guest tries to update
        update_data = {"status": "completed"}
        response = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(guest_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_update_nonexistent_enrollment(self) -> None:
        """Test that updating non-existent enrollment returns 404."""
        admin, admin_token = _register_and_login("admin")

        update_data = {"status": "completed"}
        response = client.patch(
            f"/api/v1/enrollments/{uuid.uuid4()}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 404
        assert "Enrollment not found" in response.json()["detail"]


# ===========================
# Delete Enrollment Tests (DELETE /enrollments/{id})
# ===========================


class TestDeleteEnrollment:
    """Tests for DELETE /enrollments/{id} endpoint - Admin and Teacher only."""

    def test_admin_can_delete_enrollment(self) -> None:
        """Test that admin can delete enrollment."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 204

        # Verify deletion
        get_resp = client.get(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(admin_token),
        )
        assert get_resp.status_code == 404

    def test_teacher_can_delete_enrollment(self) -> None:
        """Test that teacher can delete enrollment."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Science")
        enrollment = _create_enrollment(teacher_token, student["id"], course["id"])

        response = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 204

    def test_instructor_cannot_delete_enrollment(self) -> None:
        """Test that instructor cannot delete enrollment."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403
        assert "Only admins and teachers can delete enrollments" in response.json()["detail"]

    def test_student_cannot_delete_enrollment(self) -> None:
        """Test that student cannot delete enrollment."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Student tries to delete their own enrollment
        response = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 403

    def test_guest_cannot_delete_enrollment(self) -> None:
        """Test that guest cannot delete enrollment."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")
        guest, guest_token = _register_and_login("guest")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        response = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403

    def test_delete_nonexistent_enrollment(self) -> None:
        """Test that deleting non-existent enrollment returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.delete(
            f"/api/v1/enrollments/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Enrollment not found" in response.json()["detail"]


# ===========================
# List Enrollments by User Tests (GET /enrollments/user/{user_id})
# ===========================


class TestListEnrollmentsByUser:
    """Tests for GET /enrollments/user/{user_id} endpoint - All except Guest."""

    def test_admin_can_list_enrollments_by_user(self) -> None:
        """Test that admin can list enrollments for any user."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create courses and enrollments
        group = _create_course_group(admin_token, "Test")
        course1 = _create_course(admin_token, teacher["id"], group["id"], "Math")
        course2 = _create_course(admin_token, teacher["id"], group["id"], "Science")
        _create_enrollment(admin_token, student["id"], course1["id"])
        _create_enrollment(admin_token, student["id"], course2["id"])

        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        enrollments = response.json()
        assert isinstance(enrollments, list)
        assert len(enrollments) == 2
        # Verify course relationships are included
        course_ids = [e["course"]["id"] for e in enrollments]
        assert course1["id"] in course_ids
        assert course2["id"] in course_ids

    def test_teacher_can_list_enrollments_by_user(self) -> None:
        """Test that teacher can list enrollments for any user."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Math")
        _create_enrollment(teacher_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_instructor_can_list_enrollments_by_user(self) -> None:
        """Test that instructor can list enrollments for any user."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_student_can_list_enrollments_by_user(self) -> None:
        """Test that student can list enrollments for any user."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, _ = _register_and_login("student", "Student", "Two")

        # Create course and enrollment for student2
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student2["id"], course["id"])

        # Student1 can view student2's enrollments
        response = client.get(
            f"/api/v1/enrollments/user/{student2['id']}",
            headers=_headers(student1_token),
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_guest_cannot_list_enrollments_by_user(self) -> None:
        """Test that guest cannot list enrollments by user."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")
        guest, guest_token = _register_and_login("guest")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403
        assert "Guests cannot view user enrollments" in response.json()["detail"]

    def test_list_enrollments_for_nonexistent_user(self) -> None:
        """Test that listing enrollments for non-existent user returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/enrollments/user/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_list_enrollments_for_non_student_user(self) -> None:
        """Test that listing enrollments for non-student user returns error."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")

        response = client.get(
            f"/api/v1/enrollments/user/{teacher['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 400
        assert "Enrollments can only be listed for student users" in response.json()["detail"]

    def test_list_enrollments_by_user_empty(self) -> None:
        """Test that listing enrollments for user with no enrollments returns empty list."""
        admin, admin_token = _register_and_login("admin")
        student, _ = _register_and_login("student")

        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json() == []


# ===========================
# List Enrollments by Course Tests (GET /enrollments/course/{course_id})
# ===========================


class TestListEnrollmentsByCourse:
    """Tests for GET /enrollments/course/{course_id} endpoint - All except Guest."""

    def test_admin_can_list_enrollments_by_course(self) -> None:
        """Test that admin can list enrollments for any course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student1, _ = _register_and_login("student", "Student", "One")
        student2, _ = _register_and_login("student", "Student", "Two")

        # Create course and enrollments
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student1["id"], course["id"])
        _create_enrollment(admin_token, student2["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        enrollments = response.json()
        assert isinstance(enrollments, list)
        assert len(enrollments) == 2
        # Verify user relationships are included
        user_ids = [e["user"]["id"] for e in enrollments]
        assert student1["id"] in user_ids
        assert student2["id"] in user_ids

    def test_teacher_can_list_enrollments_by_course(self) -> None:
        """Test that teacher can list enrollments for any course."""
        teacher, teacher_token = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Science")
        _create_enrollment(teacher_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_instructor_can_list_enrollments_by_course(self) -> None:
        """Test that instructor can list enrollments for any course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_student_can_list_enrollments_by_course(self) -> None:
        """Test that student can list enrollments for any course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_guest_cannot_list_enrollments_by_course(self) -> None:
        """Test that guest cannot list enrollments by course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")
        guest, guest_token = _register_and_login("guest")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_enrollment(admin_token, student["id"], course["id"])

        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403
        assert "Guests cannot view course enrollments" in response.json()["detail"]

    def test_list_enrollments_for_nonexistent_course(self) -> None:
        """Test that listing enrollments for non-existent course returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/enrollments/course/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]

    def test_list_enrollments_by_course_empty(self) -> None:
        """Test that listing enrollments for course with no enrollments returns empty list."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")

        # Create course with no enrollments
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Empty Course")

        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json() == []


# ===========================
# Integration Tests
# ===========================


class TestEnrollmentSystemIntegration:
    """Integration tests for enrollment system scenarios."""

    def test_complete_enrollment_lifecycle(self) -> None:
        """Test complete enrollment lifecycle: create, update, delete."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")

        # Create enrollment
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])
        assert enrollment["status"] == "active"

        # Update enrollment status
        update_resp = client.patch(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(admin_token),
            json={"status": "completed"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "completed"

        # Verify in list
        list_resp = client.get("/api/v1/enrollments/", headers=_headers(admin_token))
        assert any(e["id"] == enrollment["id"] for e in list_resp.json())

        # Delete enrollment
        delete_resp = client.delete(
            f"/api/v1/enrollments/{enrollment['id']}",
            headers=_headers(admin_token),
        )
        assert delete_resp.status_code == 204

    def test_multiple_students_in_same_course(self) -> None:
        """Test multiple students enrolled in the same course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student1, _ = _register_and_login("student", "Student", "One")
        student2, _ = _register_and_login("student", "Student", "Two")
        student3, _ = _register_and_login("student", "Student", "Three")

        # Create course
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Popular Course")

        # Enroll multiple students
        _create_enrollment(admin_token, student1["id"], course["id"])
        _create_enrollment(admin_token, student2["id"], course["id"])
        _create_enrollment(admin_token, student3["id"], course["id"])

        # List enrollments by course
        response = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        enrollments = response.json()
        assert len(enrollments) == 3

    def test_student_enrolled_in_multiple_courses(self) -> None:
        """Test student enrolled in multiple courses."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create multiple courses
        group = _create_course_group(admin_token, "Test")
        course1 = _create_course(admin_token, teacher["id"], group["id"], "Math")
        course2 = _create_course(admin_token, teacher["id"], group["id"], "Science")
        course3 = _create_course(admin_token, teacher["id"], group["id"], "Art")

        # Enroll student in all courses
        _create_enrollment(admin_token, student["id"], course1["id"])
        _create_enrollment(admin_token, student["id"], course2["id"])
        _create_enrollment(admin_token, student["id"], course3["id"])

        # List enrollments by user
        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        enrollments = response.json()
        assert len(enrollments) == 3

    def test_student_self_enrollment_workflow(self) -> None:
        """Test student enrolling themselves in courses."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Create courses
        group = _create_course_group(admin_token, "Test")
        course1 = _create_course(admin_token, teacher["id"], group["id"], "Math")
        course2 = _create_course(admin_token, teacher["id"], group["id"], "Science")

        # Student enrolls themselves
        enrollment1 = _create_enrollment(student_token, student["id"], course1["id"])
        enrollment2 = _create_enrollment(student_token, student["id"], course2["id"])

        assert enrollment1["user_id"] == student["id"]
        assert enrollment2["user_id"] == student["id"]

        # Verify student can view their enrollments
        response = client.get(
            f"/api/v1/enrollments/user/{student['id']}",
            headers=_headers(student_token),
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_enrollment_status_transitions(self) -> None:
        """Test various enrollment status transitions."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        student, _ = _register_and_login("student")

        # Create course and enrollment
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math")
        enrollment = _create_enrollment(admin_token, student["id"], course["id"])

        # Test status transitions: active -> completed -> dropped -> active
        statuses = ["completed", "dropped", "active"]
        for status in statuses:
            response = client.patch(
                f"/api/v1/enrollments/{enrollment['id']}",
                headers=_headers(admin_token),
                json={"status": status},
            )
            assert response.status_code == 200
            assert response.json()["status"] == status

    def test_teacher_managing_own_course_enrollments(self) -> None:
        """Test teacher managing enrollments in their own course."""
        teacher, teacher_token = _register_and_login("teacher")
        student1, _ = _register_and_login("student", "Student", "One")
        student2, _ = _register_and_login("student", "Student", "Two")

        # Teacher creates course
        group = _create_course_group(teacher_token, "My Courses")
        course = _create_course(teacher_token, teacher["id"], group["id"], "My Math Class")

        # Teacher enrolls students
        enrollment1 = _create_enrollment(teacher_token, student1["id"], course["id"])
        enrollment2 = _create_enrollment(teacher_token, student2["id"], course["id"])

        # Teacher views course enrollments
        list_resp = client.get(
            f"/api/v1/enrollments/course/{course['id']}",
            headers=_headers(teacher_token),
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 2

        # Teacher updates enrollment status
        update_resp = client.patch(
            f"/api/v1/enrollments/{enrollment1['id']}",
            headers=_headers(teacher_token),
            json={"status": "completed"},
        )
        assert update_resp.status_code == 200

        # Teacher deletes enrollment
        delete_resp = client.delete(
            f"/api/v1/enrollments/{enrollment2['id']}",
            headers=_headers(teacher_token),
        )
        assert delete_resp.status_code == 204

    def test_different_students_different_courses(self) -> None:
        """Test complex scenario with multiple students in different courses."""
        admin, admin_token = _register_and_login("admin")
        teacher1, _ = _register_and_login("teacher", "Teacher", "One")
        teacher2, _ = _register_and_login("teacher", "Teacher", "Two")
        student1, _ = _register_and_login("student", "Student", "One")
        student2, _ = _register_and_login("student", "Student", "Two")

        # Create course groups
        group1 = _create_course_group(admin_token, "Academics")
        group2 = _create_course_group(admin_token, "Sports")

        # Create courses
        math = _create_course(admin_token, teacher1["id"], group1["id"], "Math")
        science = _create_course(admin_token, teacher1["id"], group1["id"], "Science")
        football = _create_course(admin_token, teacher2["id"], group2["id"], "Football")

        # Create enrollments
        _create_enrollment(admin_token, student1["id"], math["id"])
        _create_enrollment(admin_token, student1["id"], football["id"])
        _create_enrollment(admin_token, student2["id"], science["id"])
        _create_enrollment(admin_token, student2["id"], football["id"])

        # Verify student1 enrollments
        student1_enrollments = client.get(
            f"/api/v1/enrollments/user/{student1['id']}",
            headers=_headers(admin_token),
        ).json()
        assert len(student1_enrollments) == 2

        # Verify student2 enrollments
        student2_enrollments = client.get(
            f"/api/v1/enrollments/user/{student2['id']}",
            headers=_headers(admin_token),
        ).json()
        assert len(student2_enrollments) == 2

        # Verify football course has 2 students
        football_enrollments = client.get(
            f"/api/v1/enrollments/course/{football['id']}",
            headers=_headers(admin_token),
        ).json()
        assert len(football_enrollments) == 2

        # Verify math course has 1 student
        math_enrollments = client.get(
            f"/api/v1/enrollments/course/{math['id']}",
            headers=_headers(admin_token),
        ).json()
        assert len(math_enrollments) == 1
