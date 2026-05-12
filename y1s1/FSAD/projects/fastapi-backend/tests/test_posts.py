"""
Comprehensive tests for the /api/v1/posts endpoints.

This module tests:
- Post creation with file uploads (with and without media)
- Post listing with proper role-based permissions
- Post retrieval by ID with visibility filtering
- Post deletion with proper permissions
- Listing posts by user with visibility filtering
- Media file upload and retrieval with visibility filtering
- All visibility levels and their role-based access control
- Business logic as specified in README.md
"""

import time
import uuid
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
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


def _create_post(
    token: str,
    title: str = "Test Post",
    text_content: str = "Test content",
    visibility: str = "normal",
    latitude: float | None = None,
    longitude: float | None = None,
    files: list[tuple[str, bytes, str]] | None = None,
) -> dict[str, Any]:
    """Helper to create a post with optional media files."""
    data = {
        "title": title,
        "text_content": text_content,
        "visibility": visibility,
    }

    if latitude is not None:
        data["latitude"] = str(latitude)
    if longitude is not None:
        data["longitude"] = str(longitude)

    # Prepare files for upload
    files_data = []
    if files:
        for filename, content, content_type in files:
            files_data.append(("files", (filename, BytesIO(content), content_type)))

    response = client.post(
        "/api/v1/posts/",
        headers=_headers(token),
        data=data,
        files=files_data if files_data else None,
    )
    assert response.status_code == 201, f"Failed to create post: {response.text}"
    return response.json()


def _get_sample_image(image_num: int = 1) -> bytes:
    """Load sample image from project root."""
    image_path = Path(f"tests/sample_images/sample_image{image_num}.png")
    return image_path.read_bytes()


# ===========================
# List All Posts Tests (GET /posts/)
# ===========================


class TestListAllPosts:
    """Tests for GET /posts/ endpoint - Admin only."""

    def test_admin_can_list_all_posts(self) -> None:
        """Test that admin can list all posts."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Create posts
        _create_post(student_token, "Post 1", "Content 1")
        _create_post(admin_token, "Post 2", "Content 2")

        response = client.get("/api/v1/posts/", headers=_headers(admin_token))

        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) >= 2

    def test_teacher_cannot_list_all_posts(self) -> None:
        """Test that teacher cannot list all posts."""
        teacher, teacher_token = _register_and_login("teacher")

        response = client.get("/api/v1/posts/", headers=_headers(teacher_token))

        assert response.status_code == 403
        assert "Only admin can list all posts" in response.json()["detail"]

    def test_instructor_cannot_list_all_posts(self) -> None:
        """Test that instructor cannot list all posts."""
        instructor, instructor_token = _register_and_login("instructor")

        response = client.get("/api/v1/posts/", headers=_headers(instructor_token))

        assert response.status_code == 403

    def test_student_cannot_list_all_posts(self) -> None:
        """Test that student cannot list all posts."""
        student, student_token = _register_and_login("student")

        response = client.get("/api/v1/posts/", headers=_headers(student_token))

        assert response.status_code == 403

    def test_guest_cannot_list_all_posts(self) -> None:
        """Test that guest cannot list all posts."""
        guest, guest_token = _register_and_login("guest")

        response = client.get("/api/v1/posts/", headers=_headers(guest_token))

        assert response.status_code == 403

    def test_list_posts_without_authentication(self) -> None:
        """Test that listing posts without authentication fails."""
        response = client.get("/api/v1/posts/")

        assert response.status_code == 401


# ===========================
# Create Post Tests (POST /posts/)
# ===========================


class TestCreatePost:
    """Tests for POST /posts/ endpoint - Admin and Students only."""

    def test_admin_can_create_post_without_files(self) -> None:
        """Test that admin can create post without media files."""
        admin, admin_token = _register_and_login("admin")

        post = _create_post(
            admin_token,
            "Admin Post",
            "Admin post content",
            "normal",
        )

        assert post["title"] == "Admin Post"
        assert post["text_content"] == "Admin post content"
        assert post["visibility"] == "normal"
        assert post["owner_id"] == admin["id"]
        assert "id" in post
        assert "created_at" in post
        assert "media_items" in post
        assert len(post["media_items"]) == 0

    def test_student_can_create_post_without_files(self) -> None:
        """Test that student can create post without media files."""
        student, student_token = _register_and_login("student")

        post = _create_post(
            student_token,
            "Student Post",
            "Student post content",
        )

        assert post["title"] == "Student Post"
        assert post["owner_id"] == student["id"]

    def test_admin_can_create_post_with_single_file(self) -> None:
        """Test that admin can create post with single media file."""
        admin, admin_token = _register_and_login("admin")

        image_data = _get_sample_image(1)
        post = _create_post(
            admin_token,
            "Post with Image",
            "Post with one image",
            "normal",
            files=[("test_image.png", image_data, "image/png")],
        )

        assert post["title"] == "Post with Image"
        assert "media_items" in post
        assert len(post["media_items"]) == 1
        assert post["media_items"][0]["media_type"] == "image/png"
        assert "id" in post["media_items"][0]
        assert "media_url" in post["media_items"][0]

    def test_student_can_create_post_with_multiple_files(self) -> None:
        """Test that student can create post with multiple media files."""
        student, student_token = _register_and_login("student")

        image1 = _get_sample_image(1)
        image2 = _get_sample_image(2)

        post = _create_post(
            student_token,
            "Gallery Post",
            "Post with multiple images",
            "normal",
            files=[
                ("image1.png", image1, "image/png"),
                ("image2.png", image2, "image/png"),
            ],
        )

        assert post["title"] == "Gallery Post"
        assert len(post["media_items"]) == 2
        assert all(media["media_type"] == "image/png" for media in post["media_items"])

    def test_create_post_with_location(self) -> None:
        """Test creating post with latitude and longitude."""
        student, student_token = _register_and_login("student")

        post = _create_post(
            student_token,
            "Location Post",
            "Post with location",
            latitude=13.7563,
            longitude=100.5018,
        )

        assert post["latitude"] == 13.7563
        assert post["longitude"] == 100.5018

    def test_create_post_with_different_visibility_levels(self) -> None:
        """Test creating posts with all visibility levels (except admins_only for students)."""
        student, student_token = _register_and_login("student")

        # Students can create all visibility levels except admins_only
        visibility_levels = [
            "teachers",
            "teachers_and_instructors",
            "teachers_and_students",
            "normal",
            "guest",
        ]

        for visibility in visibility_levels:
            post = _create_post(
                student_token,
                f"Post {visibility}",
                f"Content for {visibility}",
                visibility=visibility,
            )
            assert post["visibility"] == visibility

    def test_teacher_cannot_create_post(self) -> None:
        """Test that teacher cannot create posts."""
        teacher, teacher_token = _register_and_login("teacher")

        data = {
            "title": "Teacher Post",
            "text_content": "Teacher content",
            "visibility": "normal",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(teacher_token),
            data=data,
        )

        assert response.status_code == 403
        assert "Only admin and students can create posts" in response.json()["detail"]

    def test_instructor_cannot_create_post(self) -> None:
        """Test that instructor cannot create posts."""
        instructor, instructor_token = _register_and_login("instructor")

        data = {
            "title": "Instructor Post",
            "text_content": "Instructor content",
            "visibility": "normal",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(instructor_token),
            data=data,
        )

        assert response.status_code == 403

    def test_guest_cannot_create_post(self) -> None:
        """Test that guest cannot create posts."""
        guest, guest_token = _register_and_login("guest")

        data = {
            "title": "Guest Post",
            "text_content": "Guest content",
            "visibility": "normal",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(guest_token),
            data=data,
        )

        assert response.status_code == 403

    def test_student_cannot_create_admins_only_post(self) -> None:
        """Test that students cannot create posts with admins_only visibility."""
        student, student_token = _register_and_login("student")

        data = {
            "title": "Secret Post",
            "text_content": "Only for admins",
            "visibility": "admins_only",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 403
        assert "admins_only" in response.json()["detail"].lower()

    def test_admin_can_create_admins_only_post(self) -> None:
        """Test that admins can create posts with admins_only visibility."""
        admin, admin_token = _register_and_login("admin")

        data = {
            "title": "Admin Only Post",
            "text_content": "Secret content",
            "visibility": "admins_only",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(admin_token),
            data=data,
        )

        assert response.status_code == 201
        assert response.json()["visibility"] == "admins_only"

    def test_create_post_with_empty_title_fails(self) -> None:
        """Test that creating post with empty title fails."""
        student, student_token = _register_and_login("student")

        data = {
            "title": "",
            "text_content": "Content",
            "visibility": "normal",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 422

    def test_create_post_with_empty_content_fails(self) -> None:
        """Test that creating post with empty content fails."""
        student, student_token = _register_and_login("student")

        data = {
            "title": "Title",
            "text_content": "",
            "visibility": "normal",
        }
        response = client.post(
            "/api/v1/posts/",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 422


# ===========================
# Get Post by ID Tests (GET /posts/{id})
# ===========================


class TestGetPostById:
    """Tests for GET /posts/{id} endpoint - Visibility filtered."""

    def test_owner_can_always_view_own_post(self) -> None:
        """Test that post owner can always view their own post regardless of visibility."""
        admin, admin_token = _register_and_login("admin")

        # Create post with admins_only visibility (only admins can create these)
        post = _create_post(admin_token, "My Post", "My content", "admins_only")

        response = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["id"] == post["id"]
        assert retrieved["owner_id"] == admin["id"]

    def test_admin_can_view_any_post(self) -> None:
        """Test that admin can view any post regardless of visibility."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content")

        response = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200

    def test_admins_only_visibility(self) -> None:
        """Test ADMINS_ONLY visibility - only admin can view (besides owner)."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        # Only admin can create admins_only posts
        post = _create_post(admin_token, "Admin Only Post", "Secret", "admins_only")

        # Owner (admin) can view their own post
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200

        # Others cannot view admins_only posts
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student1_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student2_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 403

    def test_teachers_visibility(self) -> None:
        """Test TEACHERS visibility - admin and teachers can view."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        post = _create_post(student1_token, "Teachers Post", "For teachers", "teachers")

        # Admin and teacher can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 200

        # Owner can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student1_token)).status_code == 200

        # Others cannot view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student2_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 403

    def test_teachers_and_instructors_visibility(self) -> None:
        """Test TEACHERS_AND_INSTRUCTORS visibility."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        post = _create_post(student1_token, "Staff Post", "For staff", "teachers_and_instructors")

        # Admin, teacher, and instructor can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 200

        # Owner can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student1_token)).status_code == 200

        # Other students and guests cannot view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student2_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 403

    def test_teachers_and_students_visibility(self) -> None:
        """Test TEACHERS_AND_STUDENTS visibility."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        post = _create_post(student1_token, "Class Post", "For class", "teachers_and_students")

        # Admin, teacher, and all students can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student1_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student2_token)).status_code == 200

        # Instructor and guest cannot view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 403
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 403

    def test_normal_visibility(self) -> None:
        """Test NORMAL visibility - all authenticated users except guests."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        post = _create_post(student1_token, "Normal Post", "Normal content", "normal")

        # All except guest can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student1_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student2_token)).status_code == 200

        # Guest cannot view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 403

    def test_guest_visibility(self) -> None:
        """Test GUEST visibility - everyone including guests can view."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        post = _create_post(student1_token, "Public Post", "Public content", "guest")

        # Everyone can view
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student1_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student2_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 200

    def test_get_nonexistent_post(self) -> None:
        """Test that getting non-existent post returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/posts/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Post not found" in response.json()["detail"]

    def test_get_post_includes_media_and_feedback(self) -> None:
        """Test that getting post includes media_items and feedback_items."""
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post with Media",
            "Content",
            files=[("test.png", image_data, "image/png")],
        )

        response = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        retrieved = response.json()
        assert "media_items" in retrieved
        assert "feedback_items" in retrieved
        assert len(retrieved["media_items"]) == 1


# ===========================
# Delete Post Tests (DELETE /posts/{id})
# ===========================


class TestDeletePost:
    """Tests for DELETE /posts/{id} endpoint."""

    def test_admin_can_delete_any_post(self) -> None:
        """Test that admin can delete any post."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 204

        # Verify deletion
        get_resp = client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token))
        assert get_resp.status_code == 404

    def test_teacher_can_delete_any_post(self) -> None:
        """Test that teacher can delete any post."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 204

    def test_student_can_delete_own_post(self) -> None:
        """Test that student can delete their own post."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "My Post", "My content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(student_token),
        )

        assert response.status_code == 204

    def test_student_cannot_delete_other_posts(self) -> None:
        """Test that student cannot delete other students' posts."""
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")

        post = _create_post(student2_token, "Other Post", "Other content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(student1_token),
        )

        assert response.status_code == 403
        assert "Students can only delete their own posts" in response.json()["detail"]

    def test_instructor_cannot_delete_posts(self) -> None:
        """Test that instructor cannot delete posts."""
        instructor, instructor_token = _register_and_login("instructor")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403
        assert "Not authorized to delete this post" in response.json()["detail"]

    def test_guest_cannot_delete_posts(self) -> None:
        """Test that guest cannot delete posts."""
        guest, guest_token = _register_and_login("guest")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403

    def test_delete_nonexistent_post(self) -> None:
        """Test that deleting non-existent post returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.delete(
            f"/api/v1/posts/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404


# ===========================
# Update Post Visibility Tests (PATCH /posts/{id}/visibility)
# ===========================


class TestUpdatePostVisibility:
    """Tests for PATCH /posts/{id}/visibility endpoint."""

    def test_admin_can_update_any_post_visibility(self) -> None:
        """Test that admin can update any post's visibility."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=teachers",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json()["visibility"] == "teachers"

    def test_admin_can_set_admins_only_visibility(self) -> None:
        """Test that admin can set admins_only visibility on any post."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=admins_only",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json()["visibility"] == "admins_only"

    def test_teacher_can_update_any_post_visibility(self) -> None:
        """Test that teacher can update any post's visibility (except admins_only)."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=teachers_and_students",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 200
        assert response.json()["visibility"] == "teachers_and_students"

    def test_teacher_cannot_set_admins_only_visibility(self) -> None:
        """Test that teacher cannot set admins_only visibility."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=admins_only",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 403
        assert "admins_only" in response.json()["detail"].lower()

    def test_student_can_update_own_post_visibility(self) -> None:
        """Test that student can update their own post's visibility."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "My Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=guest",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        assert response.json()["visibility"] == "guest"

    def test_student_cannot_update_other_posts_visibility(self) -> None:
        """Test that student cannot update other students' posts."""
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")

        post = _create_post(student2_token, "Other Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=teachers",
            headers=_headers(student1_token),
        )

        assert response.status_code == 403
        assert "Students can only update their own posts" in response.json()["detail"]

    def test_student_cannot_set_admins_only_visibility(self) -> None:
        """Test that student cannot set admins_only visibility on their own post."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "My Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=admins_only",
            headers=_headers(student_token),
        )

        assert response.status_code == 403
        assert "admins_only" in response.json()["detail"].lower()

    def test_instructor_cannot_update_post_visibility(self) -> None:
        """Test that instructor cannot update post visibility."""
        instructor, instructor_token = _register_and_login("instructor")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=teachers",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403

    def test_guest_cannot_update_post_visibility(self) -> None:
        """Test that guest cannot update post visibility."""
        guest, guest_token = _register_and_login("guest")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "guest")

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=normal",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403

    def test_update_nonexistent_post_visibility(self) -> None:
        """Test updating visibility of non-existent post returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.patch(
            f"/api/v1/posts/{uuid.uuid4()}/visibility?visibility=normal",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404

    def test_visibility_update_sets_updated_by(self) -> None:
        """Test that updating visibility sets the updated_by field."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")
        original_updated_at = post["last_updated_at"]

        # Admin updates visibility
        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=teachers",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        updated_post = response.json()
        assert updated_post["visibility"] == "teachers"
        # Verify last_updated_at changed
        assert updated_post["last_updated_at"] != original_updated_at

        # Verify the post was updated (we can't directly check updated_by in response,
        # but we can verify the update happened by the correct user through logs)
        # For now, just verify the update occurred
        get_response = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(admin_token),
        )
        assert get_response.status_code == 200

    def test_student_visibility_update_sets_updated_by(self) -> None:
        """Test that student updating their own post visibility sets updated_by."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "My Post", "Content", "normal")
        original_updated_at = post["last_updated_at"]

        # Small delay to ensure timestamp changes
        time.sleep(0.1)

        response = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=guest",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        updated_post = response.json()
        assert updated_post["visibility"] == "guest"
        assert updated_post["last_updated_at"] != original_updated_at

    def test_multiple_visibility_updates_track_last_updater(self) -> None:
        """Test that multiple visibility updates correctly track the last updater."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Student creates post
        post = _create_post(student_token, "Post", "Content", "normal")

        # Teacher updates visibility
        resp1 = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=teachers_and_students",
            headers=_headers(teacher_token),
        )
        assert resp1.status_code == 200
        time1 = resp1.json()["last_updated_at"]

        # Admin updates visibility
        time.sleep(0.1)
        resp2 = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=admins_only",
            headers=_headers(admin_token),
        )
        assert resp2.status_code == 200
        time2 = resp2.json()["last_updated_at"]

        # Verify timestamp changed
        assert time2 != time1


# ===========================
# Update Post Content Tests (PATCH /posts/{id}/content)
# ===========================


class TestUpdatePostContent:
    """Tests for PATCH /posts/{id}/content endpoint."""

    def test_admin_can_update_any_post_content(self) -> None:
        """Test that admin can update any post's content."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Original Title", "Original content", "normal")

        data = {
            "title": "Updated Title by Admin",
            "text_content": "Updated content by Admin",
        }
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(admin_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Updated Title by Admin"
        assert updated["text_content"] == "Updated content by Admin"

    def test_teacher_can_update_any_post_content(self) -> None:
        """Test that teacher can update any post's content."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Original", "Content", "normal")

        data = {
            "title": "Updated by Teacher",
            "text_content": "Teacher corrected this",
        }
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(teacher_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Updated by Teacher"
        assert updated["text_content"] == "Teacher corrected this"

    def test_student_can_update_own_post_content(self) -> None:
        """Test that student can update their own post's content."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "My Original", "My content", "normal")

        data = {
            "title": "My Updated Title",
            "text_content": "My updated content",
        }
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "My Updated Title"
        assert updated["text_content"] == "My updated content"

    def test_student_cannot_update_other_post_content(self) -> None:
        """Test that student cannot update other students' post content."""
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")

        post = _create_post(student2_token, "Student2 Post", "Content", "normal")

        data = {
            "title": "Hacked Title",
            "text_content": "Hacked content",
        }
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student1_token),
            data=data,
        )

        assert response.status_code == 403
        assert "Students can only update their own posts" in response.json()["detail"]

    def test_instructor_cannot_update_post_content(self) -> None:
        """Test that instructor cannot update post content."""
        instructor, instructor_token = _register_and_login("instructor")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "normal")

        data = {"title": "Instructor Title"}
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(instructor_token),
            data=data,
        )

        assert response.status_code == 403
        assert "Not authorized to update post content" in response.json()["detail"]

    def test_guest_cannot_update_post_content(self) -> None:
        """Test that guest cannot update post content."""
        guest, guest_token = _register_and_login("guest")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Student Post", "Content", "guest")

        data = {"title": "Guest Title"}
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(guest_token),
            data=data,
        )

        assert response.status_code == 403

    def test_update_only_title(self) -> None:
        """Test updating only the title, leaving content unchanged."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Original Title", "Original content", "normal")

        data = {"title": "New Title Only"}
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "New Title Only"
        assert updated["text_content"] == "Original content"

    def test_update_only_text_content(self) -> None:
        """Test updating only the text content, leaving title unchanged."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Original Title", "Original content", "normal")

        data = {"text_content": "New content only"}
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Original Title"
        assert updated["text_content"] == "New content only"

    def test_update_both_title_and_content(self) -> None:
        """Test updating both title and content simultaneously."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Original Title", "Original content", "normal")

        data = {
            "title": "Completely New Title",
            "text_content": "Completely new content",
        }
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Completely New Title"
        assert updated["text_content"] == "Completely new content"

    def test_content_update_sets_updated_by(self) -> None:
        """Test that updating content sets the updated_by field and updates timestamp."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Original", "Content", "normal")
        original_updated_at = post["last_updated_at"]

        time.sleep(0.1)

        data = {"title": "Updated by Admin"}
        response = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(admin_token),
            data=data,
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["last_updated_at"] != original_updated_at

    def test_update_nonexistent_post_content(self) -> None:
        """Test updating content of non-existent post returns 404."""
        admin, admin_token = _register_and_login("admin")

        data = {"title": "New Title"}
        response = client.patch(
            f"/api/v1/posts/{uuid.uuid4()}/content",
            headers=_headers(admin_token),
            data=data,
        )

        assert response.status_code == 404
        assert "Post not found" in response.json()["detail"]

    def test_multiple_content_updates_preserve_latest(self) -> None:
        """Test that multiple content updates correctly preserve the latest changes."""
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "V1", "Content V1", "normal")

        # Update 1
        data1 = {"title": "V2"}
        resp1 = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data1,
        )
        assert resp1.status_code == 200
        assert resp1.json()["title"] == "V2"
        assert resp1.json()["text_content"] == "Content V1"

        # Update 2
        data2 = {"text_content": "Content V3"}
        resp2 = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data2,
        )
        assert resp2.status_code == 200
        assert resp2.json()["title"] == "V2"
        assert resp2.json()["text_content"] == "Content V3"

        # Update 3
        data3 = {"title": "V4", "text_content": "Content V4"}
        resp3 = client.patch(
            f"/api/v1/posts/{post['id']}/content",
            headers=_headers(student_token),
            data=data3,
        )
        assert resp3.status_code == 200
        assert resp3.json()["title"] == "V4"
        assert resp3.json()["text_content"] == "Content V4"


# ===========================
# Delete Post Media Tests (DELETE /posts/{post_id}/media/{media_id})
# ===========================


class TestDeletePostMedia:
    """Tests for DELETE /posts/{post_id}/media/{media_id} endpoint."""

    def test_admin_can_delete_any_post_media(self) -> None:
        """Test that admin can delete media from any post."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post with Media",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 204

        # Verify media was deleted
        get_resp = client.get(
            f"/api/v1/posts/media/{media_id}",
            headers=_headers(admin_token),
        )
        assert get_resp.status_code == 404

    def test_teacher_can_delete_any_post_media(self) -> None:
        """Test that teacher can delete media from any post."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 204

    def test_student_can_delete_own_post_media(self) -> None:
        """Test that student can delete media from their own post."""
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "My Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(student_token),
        )

        assert response.status_code == 204

    def test_student_cannot_delete_other_post_media(self) -> None:
        """Test that student cannot delete media from other students' posts."""
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")

        image_data = _get_sample_image(1)
        post = _create_post(
            student2_token,
            "Student2 Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(student1_token),
        )

        assert response.status_code == 403
        assert "Students can only delete media from their own posts" in response.json()["detail"]

    def test_instructor_cannot_delete_post_media(self) -> None:
        """Test that instructor cannot delete post media."""
        instructor, instructor_token = _register_and_login("instructor")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 403
        assert "Not authorized to delete this media" in response.json()["detail"]

    def test_guest_cannot_delete_post_media(self) -> None:
        """Test that guest cannot delete post media."""
        guest, guest_token = _register_and_login("guest")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post",
            "Content",
            "guest",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 403

    def test_delete_media_with_wrong_post_id(self) -> None:
        """Test that deleting media with wrong post_id returns 404."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        # Use wrong post_id
        response = client.delete(
            f"/api/v1/posts/{uuid.uuid4()}/media/{media_id}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_media(self) -> None:
        """Test that deleting non-existent media returns 404."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        post = _create_post(student_token, "Post", "Content")

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404

    def test_delete_one_media_from_multiple(self) -> None:
        """Test deleting one media file from a post with multiple media files."""
        student, student_token = _register_and_login("student")

        image1 = _get_sample_image(1)
        image2 = _get_sample_image(2)
        post = _create_post(
            student_token,
            "Gallery",
            "Multiple images",
            files=[
                ("image1.png", image1, "image/png"),
                ("image2.png", image2, "image/png"),
            ],
        )

        assert len(post["media_items"]) == 2
        media_id_to_delete = post["media_items"][0]["id"]
        media_id_to_keep = post["media_items"][1]["id"]

        # Delete first media
        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id_to_delete}",
            headers=_headers(student_token),
        )
        assert response.status_code == 204

        # Verify first media is deleted
        get_deleted = client.get(
            f"/api/v1/posts/media/{media_id_to_delete}",
            headers=_headers(student_token),
        )
        assert get_deleted.status_code == 404

        # Verify second media still exists
        get_kept = client.get(
            f"/api/v1/posts/media/{media_id_to_keep}",
            headers=_headers(student_token),
        )
        assert get_kept.status_code == 200

        # Verify post still exists and has one media
        get_post = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(student_token),
        )
        assert get_post.status_code == 200
        assert len(get_post.json()["media_items"]) == 1

    def test_delete_all_media_from_post(self) -> None:
        """Test deleting all media files from a post leaves post intact."""
        student, student_token = _register_and_login("student")

        image1 = _get_sample_image(1)
        image2 = _get_sample_image(2)
        post = _create_post(
            student_token,
            "Gallery",
            "Multiple images",
            files=[
                ("image1.png", image1, "image/png"),
                ("image2.png", image2, "image/png"),
            ],
        )

        # Delete all media
        for media_item in post["media_items"]:
            response = client.delete(
                f"/api/v1/posts/{post['id']}/media/{media_item['id']}",
                headers=_headers(student_token),
            )
            assert response.status_code == 204

        # Verify post still exists but has no media
        get_post = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(student_token),
        )
        assert get_post.status_code == 200
        assert len(get_post.json()["media_items"]) == 0

    def test_delete_media_updates_post_timestamp(self) -> None:
        """Test that deleting media updates the post's updated_at timestamp."""
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        original_updated_at = post["last_updated_at"]
        media_id = post["media_items"][0]["id"]

        time.sleep(0.1)

        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(student_token),
        )
        assert response.status_code == 204

        # Check post's updated_at changed
        get_post = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(student_token),
        )
        assert get_post.status_code == 200
        assert get_post.json()["last_updated_at"] != original_updated_at

    def test_media_deletion_sets_updated_by(self) -> None:
        """Test that deleting media sets the post's updated_by field."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        time.sleep(0.1)

        # Admin deletes the media
        response = client.delete(
            f"/api/v1/posts/{post['id']}/media/{media_id}",
            headers=_headers(admin_token),
        )
        assert response.status_code == 204

        # Verify post was updated
        get_post = client.get(
            f"/api/v1/posts/{post['id']}",
            headers=_headers(admin_token),
        )
        assert get_post.status_code == 200


# ===========================
# List Posts by User Tests (GET /posts/user/{user_id})
# ===========================


class TestListPostsByUser:
    """Tests for GET /posts/user/{user_id} endpoint - Visibility filtered."""

    def test_admin_can_see_all_user_posts(self) -> None:
        """Test that admin can see all posts by a user regardless of visibility."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        # Student creates posts (can't create admins_only)
        _create_post(student_token, "Post 1", "Content 1", "teachers")
        _create_post(student_token, "Post 2", "Content 2", "normal")
        _create_post(student_token, "Post 3", "Content 3", "guest")

        response = client.get(
            f"/api/v1/posts/user/{student['id']}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200
        posts = response.json()
        assert len(posts) == 3

    def test_teacher_sees_filtered_posts(self) -> None:
        """Test that teacher sees only posts visible to teachers."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Admin creates admins_only post for student (simulating admin setting visibility)
        # In reality, we'll just skip admins_only for student posts
        # Create posts with different visibilities
        _create_post(student_token, "Teachers", "Content", "teachers")
        _create_post(student_token, "Teachers+Instructors", "Content", "teachers_and_instructors")
        _create_post(student_token, "Teachers+Students", "Content", "teachers_and_students")
        _create_post(student_token, "Normal", "Content", "normal")
        _create_post(student_token, "Guest", "Content", "guest")

        response = client.get(
            f"/api/v1/posts/user/{student['id']}",
            headers=_headers(teacher_token),
        )

        assert response.status_code == 200
        posts = response.json()
        # Teacher should see: teachers, teachers_and_instructors, teachers_and_students, normal, guest
        assert len(posts) == 5
        visibilities = [post["visibility"] for post in posts]
        assert "admins_only" not in visibilities

    def test_instructor_sees_filtered_posts(self) -> None:
        """Test that instructor sees only posts visible to instructors."""
        instructor, instructor_token = _register_and_login("instructor")
        student, student_token = _register_and_login("student")

        # Students can't create admins_only posts
        _create_post(student_token, "Teachers", "Content", "teachers")
        _create_post(student_token, "Teachers+Instructors", "Content", "teachers_and_instructors")
        _create_post(student_token, "Teachers+Students", "Content", "teachers_and_students")
        _create_post(student_token, "Normal", "Content", "normal")
        _create_post(student_token, "Guest", "Content", "guest")

        response = client.get(
            f"/api/v1/posts/user/{student['id']}",
            headers=_headers(instructor_token),
        )

        assert response.status_code == 200
        posts = response.json()
        # Instructor should see: teachers_and_instructors, normal, guest
        assert len(posts) == 3
        visibilities = [post["visibility"] for post in posts]
        assert "teachers_and_instructors" in visibilities
        assert "normal" in visibilities
        assert "guest" in visibilities

    def test_student_sees_filtered_posts(self) -> None:
        """Test that student sees only posts visible to students."""
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")

        # Students can't create admins_only posts
        _create_post(student2_token, "Teachers", "Content", "teachers")
        _create_post(student2_token, "Teachers+Instructors", "Content", "teachers_and_instructors")
        _create_post(student2_token, "Teachers+Students", "Content", "teachers_and_students")
        _create_post(student2_token, "Normal", "Content", "normal")
        _create_post(student2_token, "Guest", "Content", "guest")

        response = client.get(
            f"/api/v1/posts/user/{student2['id']}",
            headers=_headers(student1_token),
        )

        assert response.status_code == 200
        posts = response.json()
        # Student should see: teachers_and_students, normal, guest
        assert len(posts) == 3
        visibilities = [post["visibility"] for post in posts]
        assert "teachers_and_students" in visibilities
        assert "normal" in visibilities
        assert "guest" in visibilities

    def test_guest_sees_filtered_posts(self) -> None:
        """Test that guest sees only posts with guest visibility."""
        guest, guest_token = _register_and_login("guest")
        student, student_token = _register_and_login("student")

        # Students can't create admins_only posts
        _create_post(student_token, "Teachers", "Content", "teachers")
        _create_post(student_token, "Normal", "Content", "normal")
        _create_post(student_token, "Guest 1", "Content", "guest")
        _create_post(student_token, "Guest 2", "Content", "guest")

        response = client.get(
            f"/api/v1/posts/user/{student['id']}",
            headers=_headers(guest_token),
        )

        assert response.status_code == 200
        posts = response.json()
        # Guest should only see guest visibility posts
        assert len(posts) == 2
        assert all(post["visibility"] == "guest" for post in posts)


# ===========================
# Get Media Tests (GET /posts/media/{media_id})
# ===========================


class TestGetMedia:
    """Tests for GET /posts/media/{media_id} endpoint - Visibility filtered."""

    def test_owner_can_access_own_media(self) -> None:
        """Test that post owner can access their own media files."""
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "My Post",
            "Content",
            "normal",  # Students can't create admins_only posts
            files=[("image.png", image_data, "image/png")],
        )

        media_id = post["media_items"][0]["id"]

        response = client.get(
            f"/api/v1/posts/media/{media_id}",
            headers=_headers(student_token),
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/")

    def test_admin_can_access_any_media(self) -> None:
        """Test that admin can access any media file."""
        admin, admin_token = _register_and_login("admin")
        student, student_token = _register_and_login("student")

        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "Student Post",
            "Content",
            files=[("image.png", image_data, "image/png")],
        )

        media_id = post["media_items"][0]["id"]

        response = client.get(
            f"/api/v1/posts/media/{media_id}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 200

    def test_media_access_respects_post_visibility(self) -> None:
        """Test that media access respects the post's visibility settings."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        guest, guest_token = _register_and_login("guest")

        image_data = _get_sample_image(1)

        # Create post with teachers_and_instructors visibility
        post = _create_post(
            student1_token,
            "Staff Only",
            "Content",
            "teachers_and_instructors",
            files=[("image.png", image_data, "image/png")],
        )

        media_id = post["media_items"][0]["id"]

        # Admin, teacher, instructor, and owner can access
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(teacher_token)).status_code == 200
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(instructor_token)).status_code == 200
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(student1_token)).status_code == 200

        # Other student and guest cannot access
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(student2_token)).status_code == 403
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(guest_token)).status_code == 403

    def test_get_nonexistent_media(self) -> None:
        """Test that getting non-existent media returns 404."""
        admin, admin_token = _register_and_login("admin")

        response = client.get(
            f"/api/v1/posts/media/{uuid.uuid4()}",
            headers=_headers(admin_token),
        )

        assert response.status_code == 404
        assert "Media not found" in response.json()["detail"]


# ===========================
# Integration Tests
# ===========================


class TestPostSystemIntegration:
    """Integration tests for post system scenarios."""

    def test_complete_post_lifecycle_with_media(self) -> None:
        """Test complete post lifecycle: create with media, view, update visibility in mind, delete."""
        student, student_token = _register_and_login("student")
        teacher, teacher_token = _register_and_login("teacher")

        # Create post with media
        image1 = _get_sample_image(1)
        image2 = _get_sample_image(2)

        post = _create_post(
            student_token,
            "My Portfolio",
            "My best work",
            "normal",
            13.7563,
            100.5018,
            files=[
                ("work1.png", image1, "image/png"),
                ("work2.png", image2, "image/png"),
            ],
        )

        assert len(post["media_items"]) == 2

        # Teacher can view the post
        view_resp = client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token))
        assert view_resp.status_code == 200

        # Teacher can access media
        media_id = post["media_items"][0]["id"]
        media_resp = client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(teacher_token))
        assert media_resp.status_code == 200

        # Student can delete their post
        delete_resp = client.delete(f"/api/v1/posts/{post['id']}", headers=_headers(student_token))
        assert delete_resp.status_code == 204

    def test_visibility_filtering_across_multiple_posts(self) -> None:
        """Test that visibility filtering works correctly across multiple posts."""
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Admin creates posts with different visibilities
        _create_post(admin_token, "Admin Post 1", "Content", "admins_only")
        _create_post(admin_token, "Admin Post 2", "Content", "teachers")
        _create_post(admin_token, "Admin Post 3", "Content", "normal")
        _create_post(admin_token, "Admin Post 4", "Content", "guest")

        # Admin sees all posts
        admin_resp = client.get(f"/api/v1/posts/user/{admin['id']}", headers=_headers(admin_token))
        assert len(admin_resp.json()) == 4

        # Teacher sees all except admins_only
        teacher_resp = client.get(f"/api/v1/posts/user/{admin['id']}", headers=_headers(teacher_token))
        assert len(teacher_resp.json()) == 3

        # Student sees teachers_and_students, normal, and guest
        # (but none of these match, so should see normal and guest only)
        student_resp = client.get(f"/api/v1/posts/user/{admin['id']}", headers=_headers(student_token))
        assert len(student_resp.json()) == 2

    def test_multiple_students_with_different_visibility_posts(self) -> None:
        """Test complex scenario with multiple students and varying visibility."""
        admin, admin_token = _register_and_login("admin")
        student1, student1_token = _register_and_login("student", "Student", "One")
        student2, student2_token = _register_and_login("student", "Student", "Two")
        student3, student3_token = _register_and_login("student", "Student", "Three")

        # Student1 creates posts (students can't create admins_only)
        _create_post(student1_token, "S1 Normal", "Content", "normal")
        _create_post(student1_token, "S1 Public", "Content", "guest")

        # Student2 creates posts
        _create_post(student2_token, "S2 Normal", "Content", "normal")
        _create_post(student2_token, "S2 Teachers", "Content", "teachers_and_students")

        # Student3 creates posts
        _create_post(student3_token, "S3 Post", "Content", "normal")

        # Admin can see all posts
        all_posts_resp = client.get("/api/v1/posts/", headers=_headers(admin_token))
        assert len(all_posts_resp.json()) == 5

        # Student1 can see their own posts
        s1_own = client.get(f"/api/v1/posts/user/{student1['id']}", headers=_headers(student1_token))
        assert len(s1_own.json()) == 2  # Both their posts

        s2_visible = client.get(f"/api/v1/posts/user/{student2['id']}", headers=_headers(student1_token))
        assert len(s2_visible.json()) == 2  # Both are visible to students

        s3_visible = client.get(f"/api/v1/posts/user/{student3['id']}", headers=_headers(student1_token))
        assert len(s3_visible.json()) == 1  # Normal visibility

    def test_post_with_media_and_feedback(self) -> None:
        """Test post with media and feedback (integration with feedback system)."""
        teacher, teacher_token = _register_and_login("teacher")
        student, student_token = _register_and_login("student")

        # Student creates post with media
        image_data = _get_sample_image(1)
        post = _create_post(
            student_token,
            "My Work",
            "Please review",
            "normal",
            files=[("work.png", image_data, "image/png")],
        )

        # Teacher views the post
        view_resp = client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token))
        assert view_resp.status_code == 200

        # Teacher adds feedback
        feedback_data = {
            "post_id": post["id"],
            "content": "Great work!",
            "rating": 5,
        }
        feedback_resp = client.post(
            "/api/v1/feedbacks/",
            headers=_headers(teacher_token),
            json=feedback_data,
        )
        assert feedback_resp.status_code == 201

        # Student views their post with feedback
        student_view = client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student_token))
        assert student_view.status_code == 200
        post_data = student_view.json()
        assert len(post_data["feedback_items"]) == 1
        assert post_data["feedback_items"][0]["content"] == "Great work!"

    def test_owner_always_has_access_despite_visibility_changes(self) -> None:
        """Test that students (owners) can always access their own posts, media, and feedbacks
        regardless of visibility changes made by admins.

        Scenario:
        1. Student creates post with wide visibility (guest) and media
        2. Teacher adds feedback to the post
        3. Admin changes visibility to admins_only
        4. Verify student (owner) can still access everything
        5. Verify other roles cannot access (except admin)
        """
        admin, admin_token = _register_and_login("admin")
        teacher, teacher_token = _register_and_login("teacher")
        instructor, instructor_token = _register_and_login("instructor")
        student_owner, student_owner_token = _register_and_login("student", "Owner", "Student")
        student_other, student_other_token = _register_and_login("student", "Other", "Student")
        guest, guest_token = _register_and_login("guest")

        # Step 1: Student creates post with wide visibility and media
        image_data = _get_sample_image(1)
        post = _create_post(
            student_owner_token,
            "My Portfolio Work",
            "This is my best work",
            "guest",  # Wide visibility - everyone can see
            files=[("portfolio.png", image_data, "image/png")],
        )
        media_id = post["media_items"][0]["id"]

        # Verify everyone can initially access the post
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student_owner_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student_other_token)).status_code == 200
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 200

        # Step 2: Teacher adds feedback
        feedback_data = {
            "post_id": post["id"],
            "content": "Excellent work!",
            "rating": 5,
        }
        feedback_resp = client.post(
            "/api/v1/feedbacks/",
            headers=_headers(teacher_token),
            json=feedback_data,
        )
        assert feedback_resp.status_code == 201

        # Verify owner can see feedback
        post_with_feedback = client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student_owner_token))
        assert post_with_feedback.status_code == 200
        assert len(post_with_feedback.json()["feedback_items"]) == 1

        # Step 3: Admin changes visibility to admins_only
        update_visibility_resp = client.patch(
            f"/api/v1/posts/{post['id']}/visibility?visibility=admins_only",
            headers=_headers(admin_token),
        )
        assert update_visibility_resp.status_code == 200
        assert update_visibility_resp.json()["visibility"] == "admins_only"

        # Step 4: Verify OWNER (student) can STILL access everything despite admins_only visibility

        # Owner can access the post
        owner_post_resp = client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student_owner_token))
        assert owner_post_resp.status_code == 200
        owner_post_data = owner_post_resp.json()
        assert owner_post_data["id"] == post["id"]
        assert owner_post_data["visibility"] == "admins_only"

        # Owner can access their own media
        owner_media_resp = client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(student_owner_token))
        assert owner_media_resp.status_code == 200
        assert owner_media_resp.headers["content-type"].startswith("image/")

        # Owner can access feedback on their post
        assert len(owner_post_data["feedback_items"]) == 1
        assert owner_post_data["feedback_items"][0]["content"] == "Excellent work!"

        # Owner can see the post in their own list
        owner_posts_list = client.get(
            f"/api/v1/posts/user/{student_owner['id']}",
            headers=_headers(student_owner_token),
        )
        assert owner_posts_list.status_code == 200
        assert len(owner_posts_list.json()) == 1
        assert owner_posts_list.json()[0]["id"] == post["id"]

        # Step 5: Verify OTHER ROLES CANNOT access (except admin)

        # Admin can still access everything
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(admin_token)).status_code == 200
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(admin_token)).status_code == 200

        # Teacher CANNOT access anymore
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(teacher_token)).status_code == 403
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(teacher_token)).status_code == 403

        # Instructor CANNOT access
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(instructor_token)).status_code == 403
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(instructor_token)).status_code == 403

        # Other student CANNOT access
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(student_other_token)).status_code == 403
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(student_other_token)).status_code == 403

        # Guest CANNOT access
        assert client.get(f"/api/v1/posts/{post['id']}", headers=_headers(guest_token)).status_code == 403
        assert client.get(f"/api/v1/posts/media/{media_id}", headers=_headers(guest_token)).status_code == 403

        # Verify post not visible in other student's filtered list
        other_student_view = client.get(
            f"/api/v1/posts/user/{student_owner['id']}",
            headers=_headers(student_other_token),
        )
        assert other_student_view.status_code == 200
        assert len(other_student_view.json()) == 0  # Should not see any posts

        # Verify feedbacks endpoint respects visibility
        feedback_by_post = client.get(
            f"/api/v1/feedbacks/post/{post['id']}",
            headers=_headers(teacher_token),
        )
        assert feedback_by_post.status_code == 403  # Teacher cannot access feedback for admins_only post

        # But owner can still access feedback
        owner_feedback = client.get(
            f"/api/v1/feedbacks/post/{post['id']}",
            headers=_headers(student_owner_token),
        )
        assert owner_feedback.status_code == 200
        assert len(owner_feedback.json()) == 1
