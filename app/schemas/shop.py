from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Enums
class FulfillmentType(str, Enum):
    SHIPPING = 'shipping'
    PICKUP = 'pickup'
    BOTH = 'both'

class OrderStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    READY_TO_PICKUP = 'ready_to_pickup'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

# --- Products ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None # Main Image
    video_url: Optional[str] = None # New Video
    gallery: List[str] = [] # New Gallery Images
    category: Optional[str] = None
    fulfillment_type: FulfillmentType = FulfillmentType.BOTH
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None # New
    gallery: Optional[List[str]] = None # New
    category: Optional[str] = None
    fulfillment_type: Optional[FulfillmentType] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

# --- Cart ---
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    image_url: Optional[str] = None
    quantity: int
    total_price: float # Calculation field

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    cart_total: float

# --- Orders ---
class OrderCreate(BaseModel):
    delivery_method: FulfillmentType # 'shipping' or 'pickup'
    shipping_address: Optional[str] = None # Required if delivery_method is shipping

class ShopOrderItemResponse(BaseModel):
    product_name: str
    quantity: int
    price_at_purchase: float

class ShopOrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    order_status: OrderStatus
    payment_status: str
    delivery_method: FulfillmentType
    tracking_number: Optional[str]
    
    # Return Info
    return_status: Optional[str] = 'none'
    return_reason: Optional[str] = None
    
    created_at: datetime
    items: List[ShopOrderItemResponse] = []

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None

class ReturnRequest(BaseModel):
    reason: str

class ReturnProcess(BaseModel):
    status: str # approved, rejected
