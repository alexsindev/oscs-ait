"""
Comprehensive tests for the authentication system.

This module tests:
- User registration with all roles
- Input validation for registration
- Login system with JWT token generation
- JWT token usage for authenticated endpoints
- Logout and token blacklisting
- Password change functionality
- Token expiration and revocation
"""

import time
import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
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


def _register_user(
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
        "email": email or _unique_email(),
        "password": password,
        "role": role,
    }
    resp = client.post("/api/v1/auth/register", json=user_data)
    assert resp.status_code == 201, f"Failed to register user: {resp.text}"
    return resp.json()


def _login_user(email: str, password: str) -> dict[str, Any]:
    """Helper function to login a user and return the response."""
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, f"Failed to login user: {resp.text}"
    return resp.json()


def _get_auth_headers(token: str) -> dict[str, str]:
    """Helper function to create authorization headers."""
    return {"Authorization": f"Bearer {token}"}


# ===========================
# Registration Tests
# ===========================


class TestRegistration:
    """Tests for user registration endpoint."""

    def test_register_student(self) -> None:
        """Test successful registration of a student."""
        email = _unique_email("student")
        user_data = {
            "first_name": "Alice",
            "last_name": "Student",
            "email": email,
            "password": "studentpass123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert "id" in body
        assert body["first_name"] == "Alice"
        assert body["last_name"] == "Student"
        assert body["email"] == email
        assert body["role"] == "student"
        assert "password" not in body
        assert "hashed_password" not in body

    def test_register_teacher(self) -> None:
        """Test successful registration of a teacher."""
        email = _unique_email("teacher")
        user_data = {
            "first_name": "Bob",
            "last_name": "Teacher",
            "email": email,
            "password": "teacherpass123",
            "role": "teacher",
        }
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "teacher"

    def test_register_admin(self) -> None:
        """Test successful registration of an admin."""
        email = _unique_email("admin")
        user_data = {
            "first_name": "Charlie",
            "last_name": "Admin",
            "email": email,
            "password": "adminpass123",
            "role": "admin",
        }
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "admin"

    def test_register_instructor(self) -> None:
        """Test successful registration of an instructor."""
        email = _unique_email("instructor")
        user_data = {
            "first_name": "David",
            "last_name": "Instructor",
            "email": email,
            "password": "instructorpass123",
            "role": "instructor",
        }
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "instructor"

    def test_register_guest(self) -> None:
        """Test successful registration of a guest."""
        email = _unique_email("guest")
        user_data = {
            "first_name": "Eve",
            "last_name": "Guest",
            "email": email,
            "password": "guestpass123",
            "role": "guest",
        }
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "guest"

    def test_register_duplicate_email(self) -> None:
        """Test that registering with duplicate email fails."""
        email = _unique_email("duplicate")
        user_data = {
            "first_name": "First",
            "last_name": "User",
            "email": email,
            "password": "password123",
            "role": "student",
        }
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same email should fail
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Email already registered"

    def test_register_missing_first_name(self) -> None:
        """Test that registration without first_name fails."""
        user_data = {
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Unprocessable Entity

    def test_register_missing_last_name(self) -> None:
        """Test that registration without last_name fails."""
        user_data = {
            "first_name": "John",
            "email": _unique_email(),
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_missing_email(self) -> None:
        """Test that registration without email fails."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_invalid_email(self) -> None:
        """Test that registration with invalid email format fails."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "not-an-email",
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_missing_password(self) -> None:
        """Test that registration without password fails."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": _unique_email(),
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_short_password(self) -> None:
        """Test that registration with password shorter than 8 characters fails."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "short",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_long_password(self) -> None:
        """Test that registration with password longer than 100 characters fails."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "a" * 101,
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_missing_role(self) -> None:
        """Test that registration without role defaults to guest."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "password123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        # Should succeed with default role
        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "guest"  # Default role

    def test_register_invalid_role(self) -> None:
        """Test that registration with invalid role fails."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "password123",
            "role": "invalid_role",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_empty_first_name(self) -> None:
        """Test that registration with empty first_name fails."""
        user_data = {
            "first_name": "",
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_empty_last_name(self) -> None:
        """Test that registration with empty last_name fails."""
        user_data = {
            "first_name": "John",
            "last_name": "",
            "email": _unique_email(),
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_long_first_name(self) -> None:
        """Test that registration with first_name longer than 100 characters fails."""
        user_data = {
            "first_name": "a" * 101,
            "last_name": "Doe",
            "email": _unique_email(),
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_long_last_name(self) -> None:
        """Test that registration with last_name longer than 100 characters fails."""
        user_data = {
            "first_name": "John",
            "last_name": "a" * 101,
            "email": _unique_email(),
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_long_email(self) -> None:
        """Test that registration with email longer than 100 characters fails."""
        # Create an email that's too long but still valid format
        long_prefix = "a" * 92  # 92 + '@mail.com' (9) = 101 characters
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"{long_prefix}@mail.com",  # Total > 100 chars
            "password": "password123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422


# ===========================
# Login Tests
# ===========================


class TestLogin:
    """Tests for user login endpoint."""

    def test_login_success(self) -> None:
        """Test successful login returns JWT token."""
        email = _unique_email("login")
        password = "loginpass123"
        _register_user(email=email, password=password)

        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 0

    def test_login_jwt_structure(self) -> None:
        """Test that JWT token has correct structure and payload."""
        email = _unique_email("jwt")
        password = "jwtpass123"
        user = _register_user(email=email, password=password, role="teacher")

        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )

        token = response.json()["access_token"]

        # Decode without verification to check structure
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )

        assert "user_id" in decoded
        assert decoded["user_id"] == str(user["id"])
        assert "role" in decoded
        assert decoded["role"] == "teacher"
        assert "iat" in decoded
        assert "exp" in decoded
        assert "jti" in decoded

    def test_login_wrong_password(self) -> None:
        """Test login with wrong password fails."""
        email = _unique_email("wrongpass")
        _register_user(email=email, password="correctpass123")  # noqa: S106

        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": "wrongpass123"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_nonexistent_user(self) -> None:
        """Test login with non-existent email fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@mail.com", "password": "password123"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_missing_username(self) -> None:
        """Test login without username fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={"password": "password123"},
        )

        assert response.status_code == 422

    def test_login_missing_password(self) -> None:
        """Test login without password fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@mail.com"},
        )

        assert response.status_code == 422

    def test_login_different_roles(self) -> None:
        """Test that users with different roles can all login successfully."""
        roles = ["student", "teacher", "admin", "instructor", "guest"]

        for role in roles:
            email = _unique_email(role)
            password = f"{role}pass123"
            _register_user(email=email, password=password, role=role)

            response = client.post(
                "/api/v1/auth/login",
                data={"username": email, "password": password},
            )

            assert response.status_code == 200, f"Login failed for role: {role}"
            token_data = response.json()
            assert "access_token" in token_data

            # Verify role in JWT
            decoded = jwt.decode(
                token_data["access_token"],
                settings.JWT_SECRET_KEY.get_secret_value(),
                algorithms=[settings.JWT_ALGORITHM],
            )
            assert decoded["role"] == role


# ===========================
# Authenticated Endpoint Tests
# ===========================


class TestAuthenticatedEndpoints:
    """Tests for using JWT tokens to access authenticated endpoints."""

    def test_access_me_endpoint_student(self) -> None:
        """Test student can access /users/me with valid token."""
        email = _unique_email("student")
        password = "studentpass123"
        user = _register_user(email=email, password=password, role="student")
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token))

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user["id"]
        assert body["email"] == email
        assert body["role"] == "student"

    def test_access_me_endpoint_teacher(self) -> None:
        """Test teacher can access /users/me with valid token."""
        email = _unique_email("teacher")
        password = "teacherpass123"
        user = _register_user(email=email, password=password, role="teacher")
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token))

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user["id"]
        assert body["role"] == "teacher"

    def test_access_me_endpoint_admin(self) -> None:
        """Test admin can access /users/me with valid token."""
        email = _unique_email("admin")
        password = "adminpass123"
        user = _register_user(email=email, password=password, role="admin")
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token))

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user["id"]
        assert body["role"] == "admin"

    def test_access_me_endpoint_instructor(self) -> None:
        """Test instructor can access /users/me with valid token."""
        email = _unique_email("instructor")
        password = "instructorpass123"
        user = _register_user(email=email, password=password, role="instructor")
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token))

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user["id"]
        assert body["role"] == "instructor"

    def test_access_me_endpoint_guest(self) -> None:
        """Test guest can access /users/me with valid token."""
        email = _unique_email("guest")
        password = "guestpass123"
        user = _register_user(email=email, password=password, role="guest")
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token))

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == user["id"]
        assert body["role"] == "guest"

    def test_access_me_endpoint_without_token(self) -> None:
        """Test that accessing /users/me without token fails."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    def test_access_me_endpoint_invalid_token(self) -> None:
        """Test that accessing /users/me with invalid token fails."""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_access_me_endpoint_malformed_token(self) -> None:
        """Test that accessing /users/me with malformed bearer token fails."""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "InvalidFormat token"},
        )

        assert response.status_code == 401


# ===========================
# Logout Tests
# ===========================


class TestLogout:
    """Tests for logout and token blacklisting."""

    def test_logout_success(self) -> None:
        """Test successful logout."""
        email = _unique_email("logout")
        password = "logoutpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.post("/api/v1/auth/logout", headers=_get_auth_headers(token))

        assert response.status_code == 200

    def test_logout_without_token(self) -> None:
        """Test logout without token fails."""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401

    def test_logout_invalidates_token(self) -> None:
        """Test that after logout, the token cannot be used."""
        email = _unique_email("blacklist")
        password = "blacklistpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        # First, verify token works
        response1 = client.get("/api/v1/users/me", headers=_get_auth_headers(token))
        assert response1.status_code == 200

        # Logout
        logout_response = client.post("/api/v1/auth/logout", headers=_get_auth_headers(token))
        assert logout_response.status_code == 200

        # Try to use the same token again
        response2 = client.get("/api/v1/users/me", headers=_get_auth_headers(token))
        assert response2.status_code == 401
        assert "expired or revoked" in response2.json()["detail"].lower()

    def test_logout_twice(self) -> None:
        """Test that logging out twice with same token succeeds but token remains invalidated."""
        email = _unique_email("doublelogout")
        password = "doublelogoutpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        # First logout
        response1 = client.post("/api/v1/auth/logout", headers=_get_auth_headers(token))
        assert response1.status_code == 200

        # Second logout with same token should also return 200 (idempotent)
        # The logout endpoint updates the expiration if token already exists in blacklist
        response2 = client.post("/api/v1/auth/logout", headers=_get_auth_headers(token))
        assert response2.status_code == 200

    def test_login_after_logout(self) -> None:
        """Test that user can login again after logout."""
        email = _unique_email("relogin")
        password = "reloginpass123"
        _register_user(email=email, password=password)

        # First login
        login_data1 = _login_user(email, password)
        token1 = login_data1["access_token"]

        # Logout
        logout_response = client.post("/api/v1/auth/logout", headers=_get_auth_headers(token1))
        assert logout_response.status_code == 200

        # Login again
        login_data2 = _login_user(email, password)
        token2 = login_data2["access_token"]

        # New token should work
        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token2))
        assert response.status_code == 200

        # Old token should not work
        response_old = client.get("/api/v1/users/me", headers=_get_auth_headers(token1))
        assert response_old.status_code == 401


# ===========================
# Change Password Tests
# ===========================


class TestChangePassword:
    """Tests for password change functionality."""

    def test_change_password_success(self) -> None:
        """Test successful password change."""
        email = _unique_email("changepass")
        old_password = "oldpass123"
        new_password = "newpass123"
        _register_user(email=email, password=old_password)
        login_data = _login_user(email, old_password)
        token = login_data["access_token"]

        # Note: Based on the code, the endpoint only requires new password
        # The UserChangePassword model has old_password but it's not validated
        response = client.post(
            "/api/v1/auth/change_password",
            headers=_get_auth_headers(token),
            json={"old_password": old_password, "new_password": new_password},
        )

        assert response.status_code == 200

        # Try to login with old password (should fail)
        old_login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": old_password},
        )
        assert old_login.status_code == 401

        # Try to login with new password (should succeed)
        new_login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": new_password},
        )
        assert new_login.status_code == 200

    def test_change_password_without_token(self) -> None:
        """Test that changing password without token fails."""
        response = client.post(
            "/api/v1/auth/change_password",
            json={"old_password": "oldpass123", "new_password": "newpass123"},
        )

        assert response.status_code == 401

    def test_change_password_invalid_token(self) -> None:
        """Test that changing password with invalid token fails."""
        response = client.post(
            "/api/v1/auth/change_password",
            headers={"Authorization": "Bearer invalid_token"},
            json={"old_password": "oldpass123", "new_password": "newpass123"},
        )

        assert response.status_code == 401

    def test_change_password_short_new_password(self) -> None:
        """Test that changing to password shorter than 8 characters fails."""
        email = _unique_email("shortpass")
        password = "validpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.post(
            "/api/v1/auth/change_password",
            headers=_get_auth_headers(token),
            json={"old_password": password, "new_password": "short"},
        )

        assert response.status_code == 422

    def test_change_password_long_new_password(self) -> None:
        """Test that changing to password longer than 100 characters fails."""
        email = _unique_email("longpass")
        password = "validpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.post(
            "/api/v1/auth/change_password",
            headers=_get_auth_headers(token),
            json={"old_password": password, "new_password": "a" * 101},
        )

        assert response.status_code == 422

    def test_change_password_missing_new_password(self) -> None:
        """Test that changing password without new_password fails."""
        email = _unique_email("missingpass")
        password = "validpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.post(
            "/api/v1/auth/change_password",
            headers=_get_auth_headers(token),
            json={"old_password": password},
        )

        assert response.status_code == 422

    def test_change_password_after_logout(self) -> None:
        """Test that user cannot change password with invalidated token."""
        email = _unique_email("passlogout")
        password = "validpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        # Logout
        logout_response = client.post("/api/v1/auth/logout", headers=_get_auth_headers(token))
        assert logout_response.status_code == 200

        # Try to change password with invalidated token
        response = client.post(
            "/api/v1/auth/change_password",
            headers=_get_auth_headers(token),
            json={"old_password": password, "new_password": "newpass123"},
        )

        assert response.status_code == 401

    def test_change_password_wrong_old_password(self) -> None:
        """Test that changing password with wrong old password fails."""
        email = _unique_email("wrongold")
        password = "correctpass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.post(
            "/api/v1/auth/change_password",
            headers=_get_auth_headers(token),
            json={"old_password": "wrongpass123", "new_password": "newpass123"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid old password"

        # Verify old password still works
        login_check = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert login_check.status_code == 200


# ===========================
# Token Expiration Tests
# ===========================


class TestTokenExpiration:
    """Tests for JWT token expiration."""

    def test_token_has_expiration(self) -> None:
        """Test that JWT token has expiration time."""
        email = _unique_email("expire")
        password = "expirepass123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )

        assert "exp" in decoded
        assert "iat" in decoded
        # exp should be iat + ACCESS_TOKEN_EXPIRE_MINUTES * 60
        expected_exp = decoded["iat"] + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert decoded["exp"] == expected_exp

    def test_token_expiration_time_correct(self) -> None:
        """Test that token expiration time is set correctly."""
        email = _unique_email("exptime")
        password = "exptimepass123"
        before_time = int(time.time())
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        after_time = int(time.time())
        token = login_data["access_token"]

        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )

        # iat should be between before and after
        assert before_time <= decoded["iat"] <= after_time
        # exp should be iat + configured minutes
        assert decoded["exp"] == decoded["iat"] + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


# ===========================
# Additional Security Tests
# ===========================


class TestSecurityFeatures:
    """Tests for additional security features."""

    def test_password_not_returned_in_registration(self) -> None:
        """Test that password is not returned in registration response."""
        user_data = {
            "first_name": "Secure",
            "last_name": "User",
            "email": _unique_email("secure"),
            "password": "securepass123",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert "password" not in body
        assert "hashed_password" not in body

    def test_password_not_returned_in_me_endpoint(self) -> None:
        """Test that password is not returned in /users/me endpoint."""
        email = _unique_email("nopass")
        password = "nopassword123"
        _register_user(email=email, password=password)
        login_data = _login_user(email, password)
        token = login_data["access_token"]

        response = client.get("/api/v1/users/me", headers=_get_auth_headers(token))

        assert response.status_code == 200
        body = response.json()
        assert "password" not in body
        assert "hashed_password" not in body

    def test_jwt_includes_unique_jti(self) -> None:
        """Test that each JWT has a unique jti (JWT ID)."""
        email = _unique_email("jti")
        password = "jtipass123"
        _register_user(email=email, password=password)

        # Login twice
        login_data1 = _login_user(email, password)
        login_data2 = _login_user(email, password)

        token1 = login_data1["access_token"]
        token2 = login_data2["access_token"]

        decoded1 = jwt.decode(
            token1,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        decoded2 = jwt.decode(
            token2,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Each token should have different jti
        assert decoded1["jti"] != decoded2["jti"]

    def test_different_users_different_tokens(self) -> None:
        """Test that different users get different tokens."""
        email1 = _unique_email("user1")
        email2 = _unique_email("user2")
        password = "samepass123"

        _register_user(email=email1, password=password)
        _register_user(email=email2, password=password)

        login_data1 = _login_user(email1, password)
        login_data2 = _login_user(email2, password)

        token1 = login_data1["access_token"]
        token2 = login_data2["access_token"]

        # Tokens should be different
        assert token1 != token2

        # user_id in tokens should be different
        decoded1 = jwt.decode(
            token1,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        decoded2 = jwt.decode(
            token2,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )

        assert decoded1["user_id"] != decoded2["user_id"]


# ===========================
# Approve User Tests
# ===========================


class TestApproveUser:
    """Tests for the approve user endpoint."""

    def test_admin_can_approve_user(self) -> None:
        """Test that admin can approve a user."""
        # Create admin
        admin_email = _unique_email("admin")
        admin_password = "adminpass123"
        _register_user(email=admin_email, password=admin_password, role="admin")
        admin_token = _login_user(admin_email, admin_password)["access_token"]

        # Create user to be approved
        user_email = _unique_email("toapprove")
        user = _register_user(email=user_email, password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        # Verify user is not approved initially
        assert user["is_approved"] is False

        # Admin approves the user
        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(admin_token),
        )

        assert response.status_code == 200

        # Verify user is now approved
        user_token = _login_user(user_email, "userpass123")["access_token"]
        me_response = client.get("/api/v1/users/me", headers=_get_auth_headers(user_token))
        assert me_response.status_code == 200
        assert me_response.json()["is_approved"] is True

    def test_teacher_cannot_approve_user(self) -> None:
        """Test that teacher cannot approve users."""
        # Create teacher
        teacher_email = _unique_email("teacher")
        teacher_password = "teacherpass123"
        _register_user(email=teacher_email, password=teacher_password, role="teacher")
        teacher_token = _login_user(teacher_email, teacher_password)["access_token"]

        # Create user to be approved
        user = _register_user(email=_unique_email("student"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        # Teacher tries to approve
        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(teacher_token),
        )

        assert response.status_code == 403
        assert "Only admins can approve users" in response.json()["detail"]

    def test_student_cannot_approve_user(self) -> None:
        """Test that student cannot approve users."""
        # Create student
        student_email = _unique_email("student")
        student_password = "studentpass123"
        _register_user(email=student_email, password=student_password, role="student")
        student_token = _login_user(student_email, student_password)["access_token"]

        # Create another user
        user = _register_user(email=_unique_email("student2"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        # Student tries to approve
        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(student_token),
        )

        assert response.status_code == 403
        assert "Only admins can approve users" in response.json()["detail"]

    def test_instructor_cannot_approve_user(self) -> None:
        """Test that instructor cannot approve users."""
        # Create instructor
        instructor_email = _unique_email("instructor")
        instructor_password = "instructorpass123"
        _register_user(email=instructor_email, password=instructor_password, role="instructor")
        instructor_token = _login_user(instructor_email, instructor_password)["access_token"]

        # Create user
        user = _register_user(email=_unique_email("student"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        # Instructor tries to approve
        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(instructor_token),
        )

        assert response.status_code == 403
        assert "Only admins can approve users" in response.json()["detail"]

    def test_guest_cannot_approve_user(self) -> None:
        """Test that guest cannot approve users."""
        # Create guest
        guest_email = _unique_email("guest")
        guest_password = "guestpass123"
        _register_user(email=guest_email, password=guest_password, role="guest")
        guest_token = _login_user(guest_email, guest_password)["access_token"]

        # Create user
        user = _register_user(email=_unique_email("student"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        # Guest tries to approve
        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(guest_token),
        )

        assert response.status_code == 403

    def test_approve_nonexistent_user(self) -> None:
        """Test that approving non-existent user returns 404."""
        # Create admin
        admin_email = _unique_email("admin")
        admin_password = "adminpass123"
        _register_user(email=admin_email, password=admin_password, role="admin")
        admin_token = _login_user(admin_email, admin_password)["access_token"]

        # Try to approve non-existent user
        fake_user_id = uuid.uuid4()
        response = client.patch(
            f"/api/v1/auth/approve_user/{fake_user_id}",
            headers=_get_auth_headers(admin_token),
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_approve_user_without_token(self) -> None:
        """Test that approving user without authentication fails."""
        user = _register_user(email=_unique_email("student"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        response = client.patch(f"/api/v1/auth/approve_user/{user_id}")

        assert response.status_code == 401

    def test_approve_user_with_invalid_token(self) -> None:
        """Test that approving user with invalid token fails."""
        user = _register_user(email=_unique_email("student"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

    def test_approve_already_approved_user(self) -> None:
        """Test that approving an already approved user succeeds (idempotent)."""
        # Create admin
        admin_email = _unique_email("admin")
        admin_password = "adminpass123"
        _register_user(email=admin_email, password=admin_password, role="admin")
        admin_token = _login_user(admin_email, admin_password)["access_token"]

        # Create user
        user = _register_user(email=_unique_email("student"), password="userpass123", role="student")  # noqa: S106
        user_id = user["id"]

        # First approval
        response1 = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(admin_token),
        )
        assert response1.status_code == 200

        # Second approval (should also succeed)
        response2 = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(admin_token),
        )
        assert response2.status_code == 200

    def test_admin_can_approve_different_roles(self) -> None:
        """Test that admin can approve users with different roles."""
        # Create admin
        admin_email = _unique_email("admin")
        admin_password = "adminpass123"
        _register_user(email=admin_email, password=admin_password, role="admin")
        admin_token = _login_user(admin_email, admin_password)["access_token"]

        roles = ["student", "teacher", "instructor", "guest"]

        for role in roles:
            user = _register_user(
                email=_unique_email(role),
                password=f"{role}pass123",
                role=role,
            )
            user_id = user["id"]

            # Admin approves user
            response = client.patch(
                f"/api/v1/auth/approve_user/{user_id}",
                headers=_get_auth_headers(admin_token),
            )
            assert response.status_code == 200, f"Failed to approve {role}"

    def test_admin_can_approve_another_admin(self) -> None:
        """Test that admin can approve another admin."""
        # Create first admin
        admin1_email = _unique_email("admin1")
        admin1_password = "admin1pass123"
        _register_user(email=admin1_email, password=admin1_password, role="admin")
        admin1_token = _login_user(admin1_email, admin1_password)["access_token"]

        # Create second admin
        admin2 = _register_user(
            email=_unique_email("admin2"),
            password="admin2pass123",  # noqa: S106
            role="admin",
        )
        admin2_id = admin2["id"]

        # First admin approves second admin
        response = client.patch(
            f"/api/v1/auth/approve_user/{admin2_id}",
            headers=_get_auth_headers(admin1_token),
        )
        assert response.status_code == 200

    def test_student_cannot_approve_self(self) -> None:
        """Test that student cannot approve themselves."""
        # Create student
        student_email = _unique_email("student")
        student_password = "studentpass123"
        student = _register_user(email=student_email, password=student_password, role="student")
        student_token = _login_user(student_email, student_password)["access_token"]
        student_id = student["id"]

        # Student tries to approve themselves
        response = client.patch(
            f"/api/v1/auth/approve_user/{student_id}",
            headers=_get_auth_headers(student_token),
        )

        assert response.status_code == 403
        assert "Only admins can approve users" in response.json()["detail"]

    def test_approve_user_with_invalid_uuid(self) -> None:
        """Test that approving user with invalid UUID format fails."""
        # Create admin
        admin_email = _unique_email("admin")
        admin_password = "adminpass123"
        _register_user(email=admin_email, password=admin_password, role="admin")
        admin_token = _login_user(admin_email, admin_password)["access_token"]

        # Try to approve with invalid UUID
        response = client.patch(
            "/api/v1/auth/approve_user/not-a-uuid",
            headers=_get_auth_headers(admin_token),
        )

        assert response.status_code == 422

    def test_multiple_admins_can_approve_users(self) -> None:
        """Test that multiple admins can approve different users."""
        # Create two admins
        admin1 = _register_user(email=_unique_email("admin1"), password="admin1pass123", role="admin")  # noqa: S106
        admin1_token = _login_user(admin1["email"], "admin1pass123")["access_token"]

        admin2 = _register_user(email=_unique_email("admin2"), password="admin2pass123", role="admin")  # noqa: S106
        admin2_token = _login_user(admin2["email"], "admin2pass123")["access_token"]

        # Create two users
        user1 = _register_user(email=_unique_email("user1"), password="user1pass123", role="student")  # noqa: S106
        user2 = _register_user(email=_unique_email("user2"), password="user2pass123", role="student")  # noqa: S106

        # First admin approves first user
        response1 = client.patch(
            f"/api/v1/auth/approve_user/{user1['id']}",
            headers=_get_auth_headers(admin1_token),
        )
        assert response1.status_code == 200

        # Second admin approves second user
        response2 = client.patch(
            f"/api/v1/auth/approve_user/{user2['id']}",
            headers=_get_auth_headers(admin2_token),
        )
        assert response2.status_code == 200

    def test_approval_persists_after_logout(self) -> None:
        """Test that user approval status persists after logout and login."""
        # Create admin
        admin_email = _unique_email("admin")
        admin_password = "adminpass123"
        _register_user(email=admin_email, password=admin_password, role="admin")
        admin_token = _login_user(admin_email, admin_password)["access_token"]

        # Create user
        user_email = _unique_email("student")
        user_password = "studentpass123"
        user = _register_user(email=user_email, password=user_password, role="student")
        user_id = user["id"]

        # Admin approves user
        response = client.patch(
            f"/api/v1/auth/approve_user/{user_id}",
            headers=_get_auth_headers(admin_token),
        )
        assert response.status_code == 200

        # User logs in
        user_token = _login_user(user_email, user_password)["access_token"]

        # Check approval status
        me_response1 = client.get("/api/v1/users/me", headers=_get_auth_headers(user_token))
        assert me_response1.json()["is_approved"] is True

        # User logs out
        client.post("/api/v1/auth/logout", headers=_get_auth_headers(user_token))

        # User logs in again
        new_token = _login_user(user_email, user_password)["access_token"]

        # Check approval status still persists
        me_response2 = client.get("/api/v1/users/me", headers=_get_auth_headers(new_token))
        assert me_response2.json()["is_approved"] is True
