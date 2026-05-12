"""
Pytest configuration and shared fixtures for all tests.
"""

import uuid
from collections.abc import Callable, Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from loguru import logger
from sqlmodel import Session, delete

from app.db.session import get_session
from app.main import app
from app.models.auth import JWTBlacklist


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def unique_email(prefix: str = "user") -> str:
    """Generate a unique email for testing."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@mail.com"


def cleanup_database(client: TestClient) -> None:
    """Clean up all users and related data from the database."""
    # First, we need admin credentials to clean up
    # Create a temporary admin user to perform cleanup
    admin_data = {
        "first_name": "Admin",
        "last_name": "Cleanup",
        "email": unique_email("cleanup"),
        "password": "adminpass123",
        "role": "admin",
    }
    admin_resp = client.post("/api/v1/auth/register", json=admin_data)
    if admin_resp.status_code != 201:
        logger.warning("Could not create admin for cleanup")
        return

    # Login as admin
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": admin_data["email"], "password": admin_data["password"]},
    )
    if login_resp.status_code != 200:
        logger.warning("Could not login as admin for cleanup")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete feedbacks first (FK to posts and users)
    feedbacks_resp = client.get("/api/v1/feedbacks/", headers=headers)
    if feedbacks_resp.status_code == 200:
        for feedback in feedbacks_resp.json():
            fid = feedback["id"]
            delf = client.delete(f"/api/v1/feedbacks/{fid}", headers=headers)
            if delf.status_code not in (204, 404):
                logger.error(f"Failed to delete feedback {fid}: {delf.text}")

    # Delete posts (includes media cascade delete - FK to users)
    posts_resp = client.get("/api/v1/posts/", headers=headers)
    if posts_resp.status_code == 200:
        for post in posts_resp.json():
            pid = post["id"]
            delp = client.delete(f"/api/v1/posts/{pid}", headers=headers)
            if delp.status_code not in (204, 404):
                logger.error(f"Failed to delete post {pid}: {delp.text}")

    # Delete enrollments (FK to users and courses)
    enrollments_resp = client.get("/api/v1/enrollments/", headers=headers)
    if enrollments_resp.status_code == 200:
        for enrollment in enrollments_resp.json():
            eid = enrollment["id"]
            dele = client.delete(f"/api/v1/enrollments/{eid}", headers=headers)
            if dele.status_code not in (204, 404):
                logger.error(f"Failed to delete enrollment {eid}: {dele.text}")

    # Delete courses next (FK to course groups and teachers)
    courses_resp = client.get("/api/v1/courses/", headers=headers)
    if courses_resp.status_code == 200:
        for course in courses_resp.json():
            cid = course["id"]
            delc = client.delete(f"/api/v1/courses/{cid}", headers=headers)
            if delc.status_code not in (204, 404):
                logger.error(f"Failed to delete course {cid}: {delc.text}")

    # Delete course groups next
    groups_resp = client.get("/api/v1/courses/groups", headers=headers)
    if groups_resp.status_code == 200:
        for group in groups_resp.json():
            gid = group["id"]
            delg = client.delete(f"/api/v1/courses/groups/{gid}", headers=headers)
            if delg.status_code not in (204, 404):
                logger.error(f"Failed to delete course group {gid}: {delg.text}")

    # Delete student profiles (FK to users)
    profiles_resp = client.get("/api/v1/users/student_profiles", headers=headers)
    if profiles_resp.status_code == 200:
        for profile in profiles_resp.json():
            pid = profile["id"]
            delp = client.delete(f"/api/v1/users/student_profiles/{pid}", headers=headers)
            if delp.status_code != 204:
                logger.error(f"Failed to delete student profile {pid}: {delp.text}")

    # Then delete all users
    users_resp = client.get("/api/v1/users/", headers=headers)
    if users_resp.status_code == 200:
        for user in users_resp.json():
            user_id = user["id"]
            del_response = client.delete(f"/api/v1/users/{user_id}", headers=headers)
            if del_response.status_code != 204:
                logger.error(f"Failed to delete user {user_id}: {del_response.text}")

    # Clean up JWT blacklist table
    try:
        session: Session = next(get_session())
        session.exec(delete(JWTBlacklist))
        session.commit()
        logger.debug("JWT blacklist table cleaned")
    except (RuntimeError, ValueError) as e:
        logger.error(f"Failed to clean JWT blacklist: {e}")


@pytest.fixture
def clean_db(test_client: TestClient) -> Generator[None]:
    """Automatically clean database before and after each test."""
    cleanup_database(test_client)
    yield
    cleanup_database(test_client)


@pytest.fixture
def register_user(test_client: TestClient) -> Callable[[str, str, str | None, str, str], dict[str, Any]]:
    """Fixture to provide a user registration helper function."""

    def _register(
        first_name: str = "John",
        last_name: str = "Doe",
        email: str | None = None,
        password: str = "securepass123",  # noqa: S107
        role: str = "student",
    ) -> dict[str, Any]:
        """Helper function to register a user."""
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email or unique_email(),
            "password": password,
            "role": role,
        }
        resp = test_client.post("/api/v1/auth/register", json=user_data)
        assert resp.status_code == 201, f"Failed to register user: {resp.text}"
        return resp.json()

    return _register


@pytest.fixture
def login_user(test_client: TestClient) -> Callable[[str, str], dict[str, Any]]:
    """Fixture to provide a user login helper function."""

    def _login(email: str, password: str) -> dict[str, Any]:
        """Helper function to login a user and return the response."""
        resp = test_client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert resp.status_code == 200, f"Failed to login user: {resp.text}"
        return resp.json()

    return _login


@pytest.fixture
def auth_headers() -> Callable[[str], dict[str, str]]:
    """Fixture to provide a function for creating auth headers."""

    def _headers(token: str) -> dict[str, str]:
        """Helper function to create authorization headers."""
        return {"Authorization": f"Bearer {token}"}

    return _headers
