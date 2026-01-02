from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.shop import (
    ProductCreate, ProductUpdate, ProductResponse, 
    CartResponse, OrderCreate, ShopOrderResponse, OrderStatusUpdate,
    ReturnRequest, ReturnProcess
)
from app.services.shop_service import ShopService
from app.core.deps import get_current_user, role_required
from typing import List

router = APIRouter(tags=["E-commerce"])
service = ShopService()

# --- PUBLIC / PRODUCTS ---
@router.get("/shop/products")
def list_products(
    category: str = None, 
    min_price: float = None,
    max_price: float = None,
    search: str = None,
    page: int = 1,
    limit: int = 20
):
    return service.list_products(
        category=category, 
        active_only=True,
        min_price=min_price,
        max_price=max_price,
        search=search,
        page=page,
        limit=limit
    )

# --- ADMIN / PRODUCTS ---
@router.post("/shop/products", response_model=ProductResponse)
def create_product(
    data: ProductCreate, 
    current_user: dict = Depends(role_required("admin"))
):
    return service.create_product(data)

@router.put("/shop/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, 
    data: ProductUpdate,
    current_user: dict = Depends(role_required("admin"))
):
    return service.update_product(product_id, data)

@router.delete("/shop/products/{product_id}")
def delete_product(
    product_id: int,
    current_user: dict = Depends(role_required("admin"))
):
    return service.delete_product(product_id)

# --- CART ---
@router.get("/shop/cart", response_model=CartResponse)
def get_cart(current_user: dict = Depends(get_current_user)):
    return service.get_user_cart(current_user['id'])

@router.post("/shop/cart")
def add_to_cart(
    product_id: int, 
    quantity: int = 1, 
    current_user: dict = Depends(get_current_user)
):
    return service.add_to_cart(current_user['id'], product_id, quantity)

@router.delete("/shop/cart/{item_id}")
def remove_from_cart(
    item_id: int, 
    current_user: dict = Depends(get_current_user)
):
    return service.remove_from_cart(current_user['id'], item_id)

# --- ORDERS ---
@router.post("/shop/checkout")
def checkout(
    data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    return service.create_order(current_user['id'], data)

@router.get("/shop/orders", response_model=List[ShopOrderResponse])
def my_orders(current_user: dict = Depends(get_current_user)):
    return service.get_orders(user_id=current_user['id'], admin_view=False)

# --- ADMIN / ORDERS ---
@router.get("/shop/admin/orders", response_model=List[ShopOrderResponse])
def all_orders(current_user: dict = Depends(role_required("admin"))):
    return service.get_orders(admin_view=True)

@router.patch("/shop/admin/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: dict = Depends(role_required("admin"))
):
    return service.update_order_status(order_id, data.status.value, data.tracking_number)

@router.post("/shop/orders/{order_id}/return")
def request_return(order_id: int, req: ReturnRequest, current_user: dict = Depends(get_current_user)):
    return service.request_return(order_id, current_user['id'], req.reason)

@router.post("/shop/admin/orders/{order_id}/return")
def process_return(order_id: int, proc: ReturnProcess, current_user: dict = Depends(role_required("admin"))):
    return service.process_return(order_id, proc.status)

@router.get("/shop/orders/{order_id}/invoice")
def get_invoice(order_id: int, current_user: dict = Depends(get_current_user)):
    # Check ownership omitted for brevity or handled in service (TODO: security)
    html_content = service.generate_invoice(order_id)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
