import razorpay
from fastapi import HTTPException
from app.core.config import settings
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.payment import OrderCreate, PaymentVerify

class PaymentService:
    def __init__(self):
       
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, user_id: int, data: OrderCreate):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        
        amount_paise = int(data.amount * 100)

        try:
            
            order_data = {
                "amount": amount_paise,
                "currency": data.currency,
                "receipt": f"user_{user_id}",
                "payment_capture": 1 # Auto capture
            }
            order = self.client.order.create(data=order_data)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Razorpay Error: {str(e)}")

     
        sql = """
            INSERT INTO payments 
            (user_id, appointment_id, amount, currency, status, gateway_txn_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        cur.execute(sql, (
            user_id, 
            data.appointment_id, 
            data.amount, 
            data.currency, 
            'initiated', 
            order['id']
        ))
        conn.commit()

        return {
            "order": order,
            "amount": data.amount,
            "currency": data.currency,
            "key_id": settings.RAZORPAY_KEY_ID
        }

    def verify_signature(self, data: PaymentVerify):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        
        try:
            params_dict = {
                'razorpay_order_id': data.razorpay_order_id,
                'razorpay_payment_id': data.razorpay_payment_id,
                'razorpay_signature': data.razorpay_signature
            }
            self.client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
           
            cur.execute("UPDATE payments SET status='failed' WHERE gateway_txn_id=%s", (data.razorpay_order_id,))
            conn.commit()
            raise HTTPException(status_code=400, detail="Invalid Payment Signature")

       
        sql = """
            UPDATE payments 
            SET status='success', gateway_txn_id=%s 
            WHERE gateway_txn_id=%s
        """
        cur.execute(sql, (data.razorpay_payment_id, data.razorpay_order_id))
        conn.commit()

        return {"status": "success", "message": "Payment Verified"}

    def refund_payment(self, payment_id: str, amount: float = None):
        
        try:
            refund_data = {"payment_id": payment_id}
            if amount:
                refund_data["amount"] = int(amount * 100)
            
            refund = self.client.payment.refund(payment_id, refund_data) if amount else self.client.payment.refund(payment_id)
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Refund Failed: {str(e)}")

        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE payments SET status='refunded', refund_status='processed' WHERE gateway_txn_id=%s", 
            (payment_id,)
        )
        conn.commit()

        return {"status": "refunded", "refund_id": refund['id']}