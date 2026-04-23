import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
from datetime import date, time

client = TestClient(app)

@pytest.fixture
def mock_user():
    return {"id": 1, "email": "patient@example.com", "role": "patient", "full_name": "Test Patient"}

def test_book_appointment_success(mock_db_connection, mock_user):
    """Test successful appointment booking."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection
    
    # Mock return for create_pending_appointment
    # Need to mock the service layer check for provider/slots if needed
    with patch("app.api.appointments.get_current_user", return_value=mock_user):
        with patch("app.api.appointments.service") as mock_service:
            mock_service.create_pending_appointment.return_value = {
                "order": {"id": "order_123"},
                "amount": 500.0,
                "currency": "INR",
                "key_id": "rzp_test_..."
            }
            
            payload = {
                "provider_id": 1,
                "preferred_date": str(date.today()),
                "preferred_time": "10:00:00"
            }
            
            response = client.post(
                "/api/appointment/appointments/book",
                json=payload
            )
            
            assert response.status_code == 200
            assert "order" in response.json()
            mock_service.create_pending_appointment.assert_called_once()

def test_list_appointments(mock_db_connection, mock_user):
    """Test retrieving user appointments."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection
    
    with patch("app.api.appointments.get_current_user", return_value=mock_user):
        with patch("app.api.appointments.service") as mock_service:
            mock_service.list_appointments.return_value = [
                {
                    "id": 1, 
                    "provider_name": "Dr. Smith", 
                    "status": "confirmed", 
                    "preferred_slot": "2026-04-20T10:00:00",
                    "patient_id": 1,
                    "provider_id": 2,
                    "created_at": "2026-04-16T10:00:00"
                }
            ]
            
            response = client.get("/api/appointment/appointments")
            
            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]["provider_name"] == "Dr. Smith"
