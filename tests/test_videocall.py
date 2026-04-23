import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

client = TestClient(app)

def test_videocall_token_too_early(mock_db_connection):
    """Test that joining a call too early is rejected."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection
    
    # Mock appointment 1 hour in the future
    future_time = datetime.utcnow() + timedelta(hours=1)
    mock_cursor.fetchone.return_value = (future_time,)
    
    payload = {
        "channel_name": "123", # Appointment ID 123
        "uid": 0,
        "role": "publisher"
    }
    
    with patch("app.api.videocall.get_db", return_value=mock_connection):
        response = client.post(
            "/api/videocall/get-agora-token",
            json=payload
        )
        
        assert response.status_code == 403
        assert "Too early" in response.json()["detail"]

def test_videocall_token_success(mock_db_connection):
    """Test successful token generation when joining on time."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection
    
    # Mock appointment happening now
    now_time = datetime.utcnow()
    mock_cursor.fetchone.return_value = (now_time,)
    
    payload = {
        "channel_name": "123",
        "uid": 0,
        "role": "publisher"
    }
    
    with patch("app.api.videocall.get_db", return_value=mock_connection):
        with patch("app.api.videocall.RtcTokenBuilder") as mock_builder:
            mock_builder.buildTokenWithUid.return_value = "fake_agora_token"
            
            response = client.post(
                "/api/videocall/get-agora-token",
                json=payload
            )
            
            assert response.status_code == 200
            assert response.json()["token"] == "fake_agora_token"
            assert response.json()["channelName"] == "123"

def test_videocall_appointment_not_found(mock_db_connection):
    """Test rejection when appointment ID is invalid."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    
    payload = {
        "channel_name": "999",
        "uid": 0,
        "role": "publisher"
    }
    
    with patch("app.api.videocall.get_db", return_value=mock_connection):
        response = client.post(
            "/api/videocall/get-agora-token",
            json=payload
        )
        
        assert response.status_code == 404
        assert "Appointment not found" in response.json()["detail"]
