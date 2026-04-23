import pytest
import json
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_ai_chat_success(mock_db_connection):
    """Test successful AI analysis flow with mocked processing."""
    mock_conn, mock_connection, mock_cursor = mock_db_connection
    mock_cursor.lastrowid = 123
    
    # Mock image processing and LLM calls
    with patch("app.api.analysis.image_proc") as mock_image_proc:
        with patch("app.api.analysis.llm_proc") as mock_llm_proc:
            # Setup mock returns
            mock_image_proc.normalize_image_bytes.return_value = b"normalized_bits"
            mock_image_proc.validate_image_is_dermatological.return_value = (True, "Valid")
            mock_llm_proc.validate_image_is_dermatological.return_value = (True, "Valid")
            mock_image_proc.save_image_to_disk.return_value = ("unique.jpg", "uploads/unique.jpg")
            mock_image_proc.encode_image_to_base64_datauri.return_value = "data:image/jpeg;base64,..."
            
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Condition: Acne. Recommendation_Required: Yes"}}]
            }
            mock_llm_proc.call_openrouter_model.return_value = mock_response
            
            # Prepare request
            messages = json.dumps([{"role": "user", "content": "Category: Skin, Condition: Acne"}])
            files = [("image_files", ("test.jpg", b"fake_data", "image/jpeg"))]
            
            response = client.post(
                "/api/ai/chat",
                data={"messages": messages},
                files=files
            )
            
            assert response.status_code == 200
            assert "Acne" in response.json()["reply"]
            assert response.json()["recommendation_needed"] is True
            assert response.json()["chat_id"] == 123

def test_ai_chat_invalid_image():
    """Test AI analysis rejection of non-medical images."""
    with patch("app.api.analysis.llm_proc") as mock_llm_proc:
        mock_llm_proc.validate_image_is_dermatological.return_value = (False, "Not a skin photo")
        
        messages = json.dumps([{"role": "user", "content": "Category: Skin, Condition: Acne"}])
        files = [("image_files", ("cat.jpg", b"fake_cat_data", "image/jpeg"))]
        
        response = client.post(
            "/api/ai/chat",
            data={"messages": messages},
            files=files
        )
        
        assert response.status_code == 400
        assert "rejected" in response.json()["detail"]

def test_ai_chat_missing_files():
    """Test AI analysis validation for missing images."""
    messages = json.dumps([{"role": "user", "content": "Category: Skin, Condition: Acne"}])
    
    response = client.post(
        "/api/ai/chat",
        data={"messages": messages}
    )
    # FastAPI returns 422 for missing required File parameter
    assert response.status_code == 422
