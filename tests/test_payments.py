import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_payment_verify_success():
    """Test successful payment verification."""
    with patch("app.api.payment.service") as mock_service:
        mock_service.verify_signature.return_value = {"status": "success", "msg": "Payment verified"}
        
        payload = {
            "razorpay_order_id": "order_123",
            "razorpay_payment_id": "pay_123",
            "razorpay_signature": "sig_123"
        }
        
        response = client.post(
            "/api/payment/payments/verify",
            json=payload
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"

def test_refund_initiation_as_admin():
    """Test refund initiation restricted to admins."""
    admin_user = {"id": 1, "role": "admin"}
    with patch("app.api.payment.get_current_user", return_value=admin_user):
        with patch("app.api.payment.service") as mock_service:
            mock_service.refund_payment.return_value = {"msg": "Refund processed"}
            
            payload = {
                "payment_id": "pay_123",
                "amount": 500.0
            }
            
            # Using custom auth dependency mocking
            # Mocking role_required manually for simplicity in this test
            with patch("app.api.payment.role_required") as mock_role:
                mock_role.return_value = lambda x: admin_user
                
                response = client.post(
                    "/api/payment/payments/refund",
                    json=payload
                )
                
                # Note: TestClient doesn't automatically handle Depends(role_required(...)) redirection
                # but if we patch the dependency it should work.
                assert response.status_code == 200
                assert response.json()["msg"] == "Refund processed"
