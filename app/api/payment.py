from fastapi import APIRouter, Depends
from app.schemas.payment import OrderCreate, OrderResponse, PaymentVerify, PaymentStatusResponse, RefundCreate
from app.services.payment_service import PaymentService
from app.core.deps import get_current_user, role_required

router = APIRouter(tags=["Payments"])
service = PaymentService()

@router.post("/payments/create-order", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
  
    return service.create_order(user_id=current_user['id'], data=data)

@router.post("/payments/verify", response_model=PaymentStatusResponse)
def verify_payment(data: PaymentVerify):
    
    return service.verify_signature(data)

@router.post("/payments/refund")
def initiate_refund(
    data: RefundCreate,
    current_user: dict = Depends(role_required("admin"))
):
   
    return service.refund_payment(payment_id=data.payment_id, amount=data.amount)

from fastapi import Request, Header

@router.post("/payments/webhook")
async def payment_webhook(request: Request, x_razorpay_signature: str = Header(None)):
    if not x_razorpay_signature:
         pass 

    body = await request.body()
    return service.process_webhook(body, x_razorpay_signature)