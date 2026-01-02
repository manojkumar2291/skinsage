from pydantic import BaseModel
from typing import Optional


class OrderCreate(BaseModel):
    amount: float 
    currency: str = "INR"
    appointment_id: Optional[str] = None
    shop_order_id: Optional[int] = None

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class RefundCreate(BaseModel):
    payment_id: str 
    amount: Optional[float] = None 
    refund_status: Optional[str] = "requested" 


class OrderResponse(BaseModel):
    order: dict
    amount: float
    currency: str
    key_id: str

class PaymentStatusResponse(BaseModel):
    status: str
    message: str