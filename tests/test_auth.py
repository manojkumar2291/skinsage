import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_register_user(mock_auth_service):
    """Test user registration."""
    mock_auth_service.register.return_value = {"msg": "User registered successfully"}

    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User",
            "role": "patient",
            "phone_number": "1234567890"
        }
    )

    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}
    mock_auth_service.register.assert_called_once()

def test_login_user(mock_auth_service):
    """Test user login."""
    mock_auth_service.login.return_value = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "patient"
        }
    }

    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "Password123!"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "mock_refresh_token" in response.cookies.get("refresh_token")
    mock_auth_service.login.assert_called_once()

def test_generate_otp(mock_db_connection):
    """Test OTP generation."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection

    with patch("app.api.auth.send_email_sync") as mock_send_email:
        with patch("app.api.auth.get_db_connection", return_value=mock_connection):
            response = client.post(
                "/api/auth/otp/generate",
                json={"identifier": "test@example.com"}
            )

            assert response.status_code == 200
            assert response.json() == {"msg": "OTP sent successfully"}
            mock_cursor.execute.assert_called()
            mock_connection.commit.assert_called_once()

def test_verify_otp(mock_db_connection):
    """Test OTP verification."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection

    mock_cursor.fetchone.side_effect = [
        {"id": 1, "identifier": "test@example.com", "code": "123456", "is_verified": 0}, # OTP record
        {"id": 1, "email": "test@example.com", "full_name": "Test User", "role": "patient", "dob": "1990-01-01", "gender": "male"} # User record
    ]

    with patch("app.api.auth.get_db_connection", return_value=mock_connection):
        response = client.post(
            "/api/auth/otp/verify",
            json={
                "identifier": "test@example.com",
                "code": "123456"
            }
        )

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["profile_complete"] == True

def test_verify_invalid_otp(mock_db_connection):
    """Test invalid OTP."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection

    mock_cursor.fetchone.return_value = None

    with patch("app.api.auth.get_db_connection", return_value=mock_connection):
        response = client.post(
            "/api/auth/otp/verify",
            json={
                "identifier": "test@example.com",
                "code": "000000"
            }
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid or expired OTP"}
