"""
Comprehensive tests for the /api/v1/courses endpoints.

This module tests:
- Course group CRUD operations with proper role-based permissions
- Course CRUD operations with proper role-based permissions
- Listing courses within course groups
- Business logic (e.g., cannot delete course group with courses)
- Validation and edge cases
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


def _create_course_group(
    token: str,
    name: str = "Test Group",
    description: str | None = "Test Description",
) -> dict[str, Any]:
    """Helper to create a course group."""
    group_data = {
        "name": name,
        "description": description,
    }
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
    description: str | None = "Test Description",
) -> dict[str, Any]:
    """Helper to create a course."""
    course_data = {
        "name": name,
        "description": description,
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


# ===========================
# Course Group Tests
# ===========================


class TestListCourseGroups:
    """Tests for GET /courses/groups endpoint - Everyone authenticated can list."""

    def test_admin_can_list_course_groups(self) -> None:
        """Test that admin can list all course groups."""
        admin, admin_token = _register_and_login("admin")
        _create_course_group(admin_token, "Academics")
        _create_course_group(admin_token, "Sports")

        response = client.get("/api/v1/courses/groups", headers=_headers(admin_token))

        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        assert len(groups) >= 2
        group_names = [g["name"] for g in groups]
        assert "Academics" in group_names
        assert "Sports" in group_names

    def test_teacher_can_list_course_groups(self) -> None:
        """Test that teacher can list course groups."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        _create_course_group(admin_token, "Music")

        response = client.get("/api/v1/courses/groups", headers=_headers(teacher_token))

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_instructor_can_list_course_groups(self) -> None:
        """Test that instructor can list course groups."""
        instructor, instructor_token = _register_and_login("instructor")

        response = client.get("/api/v1/courses/groups", headers=_headers(instructor_token))

        assert response.status_code == 200

    def test_student_can_list_course_groups(self) -> None:
        """Test that student can list course groups."""
        student, student_token = _register_and_login("student")

        response = client.get("/api/v1/courses/groups", headers=_headers(student_token))

        assert response.status_code == 200

    def test_guest_can_list_course_groups(self) -> None:
        """Test that guest can list course groups."""
        guest, guest_token = _register_and_login("guest")

        response = client.get("/api/v1/courses/groups", headers=_headers(guest_token))

        assert response.status_code == 200

    def test_list_course_groups_without_authentication(self) -> None:
        """Test that listing course groups without authentication fails."""
        response = client.get("/api/v1/courses/groups")

        assert response.status_code == 401


class TestCreateCourseGroup:
    """Tests for POST /courses/groups endpoint - Admin and Teacher only."""

    def test_admin_can_create_course_group(self) -> None:
        """Test that admin can create a course group."""
        admin, admin_token = _register_and_login("admin")

        group_data = {
            "name": "Academics",
            "description": "Academic courses",
        }
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(admin_token),
            json=group_data,
        )

        assert response.status_code == 201
        group = response.json()
        assert group["name"] == "Academics"
        assert group["description"] == "Academic courses"
        assert "id" in group

    def test_teacher_can_create_course_group(self) -> None:
        """Test that teacher can create a course group."""
        teacher, teacher_token = _register_and_login("teacher")

        group_data = {
            "name": "Sports",
            "description": "Sports activities",
        }
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(teacher_token),
            json=group_data,
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Sports"

    def test_instructor_cannot_create_course_group(self) -> None:
        """Test that instructor cannot create course groups."""
        instructor, instructor_token = _register_and_login("instructor")

        group_data = {"name": "Test", "description": "Test"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(instructor_token),
            json=group_data,
        )

        assert response.status_code == 403
        assert "Only admins and teachers" in response.json()["detail"]

    def test_student_cannot_create_course_group(self) -> None:
        """Test that student cannot create course groups."""
        student, student_token = _register_and_login("student")

        group_data = {"name": "Test", "description": "Test"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(student_token),
            json=group_data,
        )

        assert response.status_code == 403

    def test_guest_cannot_create_course_group(self) -> None:
        """Test that guest cannot create course groups."""
        guest, guest_token = _register_and_login("guest")

        group_data = {"name": "Test", "description": "Test"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(guest_token),
            json=group_data,
        )

        assert response.status_code == 403

    def test_create_course_group_with_duplicate_name(self) -> None:
        """Test that creating course group with duplicate name fails."""
        admin, admin_token = _register_and_login("admin")
        _create_course_group(admin_token, "Academics")

        # Try to create another with same name
        group_data = {"name": "Academics", "description": "Different description"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(admin_token),
            json=group_data,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_course_group_with_optional_description(self) -> None:
        """Test that description is optional when creating course group."""
        admin, admin_token = _register_and_login("admin")

        group_data = {"name": "No Description Group"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(admin_token),
            json=group_data,
        )

        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_create_course_group_with_empty_name(self) -> None:
        """Test that creating course group with empty name fails."""
        admin, admin_token = _register_and_login("admin")

        group_data = {"name": "", "description": "Test"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(admin_token),
            json=group_data,
        )

        assert response.status_code == 422

    def test_create_course_group_with_long_name(self) -> None:
        """Test that creating course group with name longer than 100 chars fails."""
        admin, admin_token = _register_and_login("admin")

        group_data = {"name": "a" * 101, "description": "Test"}
        response = client.post(
            "/api/v1/courses/groups",
            headers=_headers(admin_token),
            json=group_data,
        )

        assert response.status_code == 422


class TestGetCourseGroup:
    """Tests for GET /courses/groups/{id} endpoint - Everyone authenticated can read."""

    def test_admin_can_get_course_group(self) -> None:
        """Test that admin can get course group details."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "Academics", "Academic courses")

        response = client.get(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == group["id"]
        assert retrieved["name"] == "Academics"

    def test_all_roles_can_get_course_group(self) -> None:
        """Test that all roles can get course group details."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "Sports")

        for role in ["teacher", "instructor", "student", "guest"]:
            _, token = _register_and_login(role)
            response = client.get(
                f"/api/v1/courses/groups/{group['id']}",
                headers=_headers(token),
            )
            assert response.status_code == 200, f"Role {role} failed"

    def test_get_nonexistent_course_group(self) -> None:
        """Test that getting non-existent course group returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/courses/groups/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Course group not found" in response.json()["detail"]


class TestUpdateCourseGroup:
    """Tests for PATCH /courses/groups/{id} endpoint - Admin and Teacher only."""

    def test_admin_can_update_course_group(self) -> None:
        """Test that admin can update course group."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "Original", "Original description")

        update_data = {
            "name": "Updated",
            "description": "Updated description",
        }
        response = client.patch(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Updated"
        assert updated["description"] == "Updated description"

    def test_teacher_can_update_course_group(self) -> None:
        """Test that teacher can update course group."""
        teacher, teacher_token = _register_and_login("teacher")
        group = _create_course_group(teacher_token, "Original")

        update_data = {"name": "Updated by teacher"}
        response = client.patch(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(teacher_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated by teacher"

    def test_instructor_cannot_update_course_group(self) -> None:
        """Test that instructor cannot update course groups."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        group = _create_course_group(admin_token, "Test")

        update_data = {"name": "Hacked"}
        response = client.patch(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(instructor_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_student_cannot_update_course_group(self) -> None:
        """Test that student cannot update course groups."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")
        group = _create_course_group(admin_token, "Test")

        update_data = {"name": "Hacked"}
        response = client.patch(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(student_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_update_course_group_partial_fields(self) -> None:
        """Test that updating course group with partial fields works."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "Original", "Original description")

        # Update only name
        update_data = {"name": "Updated Name"}
        response = client.patch(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "Original description"  # Unchanged

    def test_update_nonexistent_course_group(self) -> None:
        """Test that updating non-existent course group returns 404."""
        admin, admin_token = _register_and_login("admin")

        update_data = {"name": "Updated"}
        response = client.patch(
            f"/api/v1/courses/groups/{uuid.uuid4()}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 404


class TestDeleteCourseGroup:
    """Tests for DELETE /courses/groups/{id} endpoint - Admin and Teacher only."""

    def test_admin_can_delete_empty_course_group(self) -> None:
        """Test that admin can delete course group without courses."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "To Delete")

        response = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 204

        # Verify deletion
        get_resp = client.get(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
        )
        assert get_resp.status_code == 404

    def test_teacher_can_delete_empty_course_group(self) -> None:
        """Test that teacher can delete course group without courses."""
        teacher, teacher_token = _register_and_login("teacher")
        group = _create_course_group(teacher_token, "To Delete")

        response = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 204

    def test_cannot_delete_course_group_with_courses(self) -> None:
        """Test that deleting course group with courses fails."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Has Courses")
        _create_course(admin_token, teacher["id"], group["id"], "Math")

        response = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 400
        assert "still has courses" in response.json()["detail"]

    def test_instructor_cannot_delete_course_group(self) -> None:
        """Test that instructor cannot delete course groups."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        group = _create_course_group(admin_token, "Test")

        response = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403

    def test_student_cannot_delete_course_group(self) -> None:
        """Test that student cannot delete course groups."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")
        group = _create_course_group(admin_token, "Test")

        response = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 403

    def test_delete_nonexistent_course_group(self) -> None:
        """Test that deleting non-existent course group returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.delete(
            f"/api/v1/courses/groups/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404


# ===========================
# Course Tests
# ===========================


class TestListCourses:
    """Tests for GET /courses/ endpoint - Everyone authenticated can list."""

    def test_admin_can_list_courses(self) -> None:
        """Test that admin can list all courses."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Academics")
        _create_course(admin_token, teacher["id"], group["id"], "Math")
        _create_course(admin_token, teacher["id"], group["id"], "Science")

        response = client.get("/api/v1/courses/", headers=_headers(admin_token))

        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)
        assert len(courses) >= 2
        course_names = [c["name"] for c in courses]
        assert "Math" in course_names
        assert "Science" in course_names

    def test_all_roles_can_list_courses(self) -> None:
        """Test that all roles can list courses."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")
        _create_course(admin_token, teacher["id"], group["id"], "Test Course")

        for role in ["teacher", "instructor", "student", "guest"]:
            _, token = _register_and_login(role)
            response = client.get("/api/v1/courses/", headers=_headers(token))
            assert response.status_code == 200, f"Role {role} failed"
            assert isinstance(response.json(), list)

    def test_list_courses_without_authentication(self) -> None:
        """Test that listing courses without authentication fails."""
        response = client.get("/api/v1/courses/")

        assert response.status_code == 401


class TestCreateCourse:
    """Tests for POST /courses/ endpoint - Admin and Teacher only."""

    def test_admin_can_create_course(self) -> None:
        """Test that admin can create a course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Academics")

        course_data = {
            "name": "Mathematics",
            "description": "Advanced mathematics",
            "teacher_id": teacher["id"],
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(admin_token),
            json=course_data,
        )

        assert response.status_code == 201
        course = response.json()
        assert course["name"] == "Mathematics"
        assert course["description"] == "Advanced mathematics"
        assert course["teacher_id"] == teacher["id"]
        assert course["course_group_id"] == group["id"]
        assert "id" in course

    def test_teacher_can_create_course(self) -> None:
        """Test that teacher can create a course."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Sports")

        course_data = {
            "name": "Football",
            "description": "Football training",
            "teacher_id": teacher["id"],
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(teacher_token),
            json=course_data,
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Football"

    def test_instructor_cannot_create_course(self) -> None:
        """Test that instructor cannot create courses."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        group = _create_course_group(admin_token, "Test")

        course_data = {
            "name": "Test",
            "teacher_id": instructor["id"],
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(instructor_token),
            json=course_data,
        )

        assert response.status_code == 403
        assert "Only admins and teachers" in response.json()["detail"]

    def test_student_cannot_create_course(self) -> None:
        """Test that student cannot create courses."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")
        group = _create_course_group(admin_token, "Test")

        course_data = {
            "name": "Test",
            "teacher_id": admin["id"],
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(student_token),
            json=course_data,
        )

        assert response.status_code == 403

    def test_create_course_with_duplicate_name(self) -> None:
        """Test that creating course with duplicate name fails."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")
        _create_course(admin_token, teacher["id"], group["id"], "Math")

        # Try to create another with same name
        course_data = {
            "name": "Math",
            "description": "Different",
            "teacher_id": teacher["id"],
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(admin_token),
            json=course_data,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_course_with_nonexistent_course_group(self) -> None:
        """Test that creating course with non-existent course group fails."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")

        course_data = {
            "name": "Test",
            "teacher_id": teacher["id"],
            "course_group_id": str(uuid.uuid4()),
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(admin_token),
            json=course_data,
        )

        assert response.status_code == 404
        assert "Course group not found" in response.json()["detail"]

    def test_create_course_with_nonexistent_teacher(self) -> None:
        """Test that creating course with non-existent teacher fails."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "Test")

        course_data = {
            "name": "Test",
            "teacher_id": str(uuid.uuid4()),
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(admin_token),
            json=course_data,
        )

        assert response.status_code == 404
        assert "Teacher not found" in response.json()["detail"]

    def test_create_course_with_optional_description(self) -> None:
        """Test that description is optional when creating course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")

        course_data = {
            "name": "No Description",
            "teacher_id": teacher["id"],
            "course_group_id": group["id"],
        }
        response = client.post(
            "/api/v1/courses/",
            headers=_headers(admin_token),
            json=course_data,
        )

        assert response.status_code == 201
        assert response.json()["description"] is None


class TestGetCourse:
    """Tests for GET /courses/{id} endpoint - Everyone authenticated can read."""

    def test_admin_can_get_course(self) -> None:
        """Test that admin can get course details."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Academics")
        course = _create_course(admin_token, teacher["id"], group["id"], "Math", "Mathematics course")

        response = client.get(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == course["id"]
        assert retrieved["name"] == "Math"
        assert retrieved["description"] == "Mathematics course"

    def test_all_roles_can_get_course(self) -> None:
        """Test that all roles can get course details."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Test")

        for role in ["teacher", "instructor", "student", "guest"]:
            _, token = _register_and_login(role)
            response = client.get(
                f"/api/v1/courses/{course['id']}",
                headers=_headers(token),
            )
            assert response.status_code == 200, f"Role {role} failed"

    def test_get_nonexistent_course(self) -> None:
        """Test that getting non-existent course returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/courses/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Course not found" in response.json()["detail"]


class TestUpdateCourse:
    """Tests for PATCH /courses/{id} endpoint - Admin and Teacher only."""

    def test_admin_can_update_course(self) -> None:
        """Test that admin can update course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Academics")
        course = _create_course(admin_token, teacher["id"], group["id"], "Original", "Original desc")

        update_data = {
            "name": "Updated",
            "description": "Updated description",
        }
        response = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Updated"
        assert updated["description"] == "Updated description"

    def test_teacher_can_update_course(self) -> None:
        """Test that teacher can update course."""
        teacher, teacher_token = _register_and_login("teacher")
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "Original")

        update_data = {"name": "Updated by teacher"}
        response = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(teacher_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated by teacher"

    def test_instructor_cannot_update_course(self) -> None:
        """Test that instructor cannot update courses."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, admin["id"], group["id"], "Test")

        update_data = {"name": "Hacked"}
        response = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(instructor_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_student_cannot_update_course(self) -> None:
        """Test that student cannot update courses."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, admin["id"], group["id"], "Test")

        update_data = {"name": "Hacked"}
        response = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(student_token),
            json=update_data,
        )

        assert response.status_code == 403

    def test_update_course_change_group(self) -> None:
        """Test that course can be moved to different group."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group1 = _create_course_group(admin_token, "Academics")
        group2 = _create_course_group(admin_token, "Sports")
        course = _create_course(admin_token, teacher["id"], group1["id"], "Math")

        update_data = {"course_group_id": group2["id"]}
        response = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["course_group_id"] == group2["id"]

    def test_update_course_partial_fields(self) -> None:
        """Test that updating course with partial fields works."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "Original", "Original desc")

        # Update only name
        update_data = {"name": "Updated Name"}
        response = client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "Original desc"  # Unchanged

    def test_update_nonexistent_course(self) -> None:
        """Test that updating non-existent course returns 404."""
        admin, admin_token = _register_and_login("admin")

        update_data = {"name": "Updated"}
        response = client.patch(
            f"/api/v1/courses/{uuid.uuid4()}",
            headers=_headers(admin_token),
            json=update_data,
        )

        assert response.status_code == 404


class TestDeleteCourse:
    """Tests for DELETE /courses/{id} endpoint - Admin and Teacher only."""

    def test_admin_can_delete_course(self) -> None:
        """Test that admin can delete course."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, teacher["id"], group["id"], "To Delete")

        response = client.delete(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 204

        # Verify deletion
        get_resp = client.get(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
        )
        assert get_resp.status_code == 404

    def test_teacher_can_delete_course(self) -> None:
        """Test that teacher can delete course."""
        teacher, teacher_token = _register_and_login("teacher")
        group = _create_course_group(teacher_token, "Test")
        course = _create_course(teacher_token, teacher["id"], group["id"], "To Delete")

        response = client.delete(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 204

    def test_instructor_cannot_delete_course(self) -> None:
        """Test that instructor cannot delete courses."""
        admin, admin_token = _register_and_login("admin")
        instructor, instructor_token = _register_and_login("instructor")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, admin["id"], group["id"], "Test")

        response = client.delete(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403

    def test_student_cannot_delete_course(self) -> None:
        """Test that student cannot delete courses."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")
        group = _create_course_group(admin_token, "Test")
        course = _create_course(admin_token, admin["id"], group["id"], "Test")

        response = client.delete(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 403

    def test_delete_nonexistent_course(self) -> None:
        """Test that deleting non-existent course returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.delete(
            f"/api/v1/courses/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404


class TestListCoursesInGroup:
    """Tests for GET /courses/groups/{id}/courses endpoint."""

    def test_list_courses_in_group(self) -> None:
        """Test that listing courses in a group works."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        academics = _create_course_group(admin_token, "Academics")
        sports = _create_course_group(admin_token, "Sports")

        # Create courses in different groups
        _create_course(admin_token, teacher["id"], academics["id"], "Math")
        _create_course(admin_token, teacher["id"], academics["id"], "Science")
        _create_course(admin_token, teacher["id"], sports["id"], "Football")

        response = client.get(
            f"/api/v1/courses/groups/{academics['id']}/courses",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)
        assert len(courses) == 2
        course_names = [c["name"] for c in courses]
        assert "Math" in course_names
        assert "Science" in course_names
        assert "Football" not in course_names

    def test_all_roles_can_list_courses_in_group(self) -> None:
        """Test that all roles can list courses in a group."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")
        group = _create_course_group(admin_token, "Test")
        _create_course(admin_token, teacher["id"], group["id"], "Test")

        for role in ["teacher", "instructor", "student", "guest"]:
            _, token = _register_and_login(role)
            response = client.get(
                f"/api/v1/courses/groups/{group['id']}/courses",
                headers=_headers(token),
            )
            assert response.status_code == 200, f"Role {role} failed"

    def test_list_courses_in_empty_group(self) -> None:
        """Test that listing courses in empty group returns empty list."""
        admin, admin_token = _register_and_login("admin")
        group = _create_course_group(admin_token, "Empty Group")

        response = client.get(
            f"/api/v1/courses/groups/{group['id']}/courses",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_list_courses_in_nonexistent_group(self) -> None:
        """Test that listing courses in non-existent group returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/courses/groups/{uuid.uuid4()}/courses",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Course group not found" in response.json()["detail"]


# ===========================
# Integration Tests
# ===========================


class TestCourseSystemIntegration:
    """Integration tests for course system scenarios."""

    def test_complete_course_group_lifecycle(self) -> None:
        """Test creating, updating, and managing a course group with courses."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")

        # Create course group
        group = _create_course_group(admin_token, "Academics", "Academic courses")

        # Create multiple courses in the group
        math = _create_course(admin_token, teacher["id"], group["id"], "Math", "Mathematics")
        science = _create_course(admin_token, teacher["id"], group["id"], "Science", "Science course")

        # List courses in group
        response = client.get(
            f"/api/v1/courses/groups/{group['id']}/courses",
            headers=_headers(admin_token),
        )
        assert len(response.json()) == 2

        # Update course group name
        client.patch(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
            json={"name": "Core Academics"},
        )

        # Try to delete group with courses - should fail
        delete_resp = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
        )
        assert delete_resp.status_code == 400

        # Delete courses first
        client.delete(f"/api/v1/courses/{math['id']}", headers=_headers(admin_token))
        client.delete(f"/api/v1/courses/{science['id']}", headers=_headers(admin_token))

        # Now can delete group
        delete_resp2 = client.delete(
            f"/api/v1/courses/groups/{group['id']}",
            headers=_headers(admin_token),
        )
        assert delete_resp2.status_code == 204

    def test_multiple_groups_with_courses(self) -> None:
        """Test managing multiple course groups with their courses."""
        admin, admin_token = _register_and_login("admin")
        teacher1, _ = _register_and_login("teacher", "Teacher", "One")
        teacher2, _ = _register_and_login("teacher", "Teacher", "Two")

        # Create multiple groups
        academics = _create_course_group(admin_token, "Academics", "Academic subjects")
        sports = _create_course_group(admin_token, "Sports", "Sports activities")
        arts = _create_course_group(admin_token, "Arts", "Arts and culture")

        # Create courses in each group
        _create_course(admin_token, teacher1["id"], academics["id"], "Math")
        _create_course(admin_token, teacher1["id"], academics["id"], "Science")
        _create_course(admin_token, teacher2["id"], sports["id"], "Football")
        _create_course(admin_token, teacher2["id"], sports["id"], "Basketball")
        _create_course(admin_token, teacher1["id"], arts["id"], "Painting")

        # Verify all groups exist
        groups_resp = client.get("/api/v1/courses/groups", headers=_headers(admin_token))
        assert len(groups_resp.json()) == 3

        # Verify all courses exist
        courses_resp = client.get("/api/v1/courses/", headers=_headers(admin_token))
        assert len(courses_resp.json()) == 5

        # Verify courses in each group
        academics_courses = client.get(
            f"/api/v1/courses/groups/{academics['id']}/courses",
            headers=_headers(admin_token),
        )
        assert len(academics_courses.json()) == 2

        sports_courses = client.get(
            f"/api/v1/courses/groups/{sports['id']}/courses",
            headers=_headers(admin_token),
        )
        assert len(sports_courses.json()) == 2

    def test_move_course_between_groups(self) -> None:
        """Test moving a course from one group to another."""
        admin, admin_token = _register_and_login("admin")
        teacher, _ = _register_and_login("teacher")

        group1 = _create_course_group(admin_token, "Group 1")
        group2 = _create_course_group(admin_token, "Group 2")

        # Create course in group1
        course = _create_course(admin_token, teacher["id"], group1["id"], "Moving Course")

        # Verify it's in group1
        group1_courses = client.get(
            f"/api/v1/courses/groups/{group1['id']}/courses",
            headers=_headers(admin_token),
        )
        assert len(group1_courses.json()) == 1

        # Move to group2
        client.patch(
            f"/api/v1/courses/{course['id']}",
            headers=_headers(admin_token),
            json={"course_group_id": group2["id"]},
        )

        # Verify it's now in group2 and not in group1
        group1_courses_after = client.get(
            f"/api/v1/courses/groups/{group1['id']}/courses",
            headers=_headers(admin_token),
        )
        assert len(group1_courses_after.json()) == 0

        group2_courses = client.get(
            f"/api/v1/courses/groups/{group2['id']}/courses",
            headers=_headers(admin_token),
        )
        assert len(group2_courses.json()) == 1
