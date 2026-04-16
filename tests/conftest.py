import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

# Create a test client
client = TestClient(app)

@pytest.fixture
def mock_db_connection():
    """Fixture to mock database connection to prevent actual DB writes during testing."""
    with patch("app.database.mysql_conn.get_db_connection") as mock_conn:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_connection
        yield mock_conn, mock_connection, mock_cursor

@pytest.fixture
def mock_auth_service():
    """Fixture to mock the AuthService."""
    with patch("app.api.auth.service") as mock_service:
        yield mock_service
