from app.database.mysql_conn import get_db_connection
from app.schemas.shop import ProductCreate, ProductUpdate, FulfillmentType, OrderCreate, OrderStatus
from fastapi import HTTPException
import mysql.connector

class ShopService:
    
    # --- PRODUCTS ---
    def create_product(self, data: ProductCreate):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                INSERT INTO products (name, description, price, discount_price, stock_quantity, image_url, video_url, category, fulfillment_type, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (data.name, data.description, data.price, data.discount_price, data.stock_quantity, data.image_url, data.video_url, data.category, data.fulfillment_type.value, data.is_active))
            new_id = cursor.lastrowid
            
            # Insert Gallery
            if data.gallery:
                gallery_sql = "INSERT INTO product_gallery (product_id, image_url) VALUES (%s, %s)"
                for img in data.gallery:
                    cursor.execute(gallery_sql, (new_id, img))
            
            conn.commit()
            
            # Fetch back
            cursor.execute("SELECT * FROM products WHERE id=%s", (new_id,))
            prod = cursor.fetchone()
            
            # Fetch Gallery
            cursor.execute("SELECT image_url FROM product_gallery WHERE product_id=%s", (new_id,))
            gallery = [row['image_url'] for row in cursor.fetchall()]
            prod['gallery'] = gallery
            return prod
        finally:
            cursor.close()
            conn.close()

    def list_products(self, category: str = None, active_only: bool = True, 
                      min_price: float = None, max_price: float = None, 
                      search: str = None, page: int = 1, limit: int = 20):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            # Base Query
            sql = "SELECT SQL_CALC_FOUND_ROWS * FROM products WHERE 1=1"
            params = []
            
            # 1. Filters
            if active_only:
                sql += " AND is_active = 1"
            if category:
                sql += " AND category = %s"
                params.append(category)
            if min_price is not None:
                sql += " AND price >= %s"
                params.append(min_price)
            if max_price is not None:
                sql += " AND price <= %s"
                params.append(max_price)
            if search:
                sql += " AND (name LIKE %s OR description LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
                
            # 2. Pagination
            offset = (page - 1) * limit
            sql += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
                
            cursor.execute(sql, params)
            products = cursor.fetchall()
            
            # Get Total Count
            cursor.execute("SELECT FOUND_ROWS() as total")
            total_count = cursor.fetchone()['total']
            
            cursor.close()
            
            if not products:
                return {
                    "products": [],
                    "total": 0,
                    "page": page,
                    "limit": limit,
                    "total_pages": 0
                }
                
            # Fetch Galleries
            pids = [p['id'] for p in products]
            if pids:
                format_strings = ','.join(['%s'] * len(pids))
                cursor_g = conn.cursor(dictionary=True, buffered=True)
                cursor_g.execute(f"SELECT product_id, image_url FROM product_gallery WHERE product_id IN ({format_strings})", tuple(pids))
                galleries = cursor_g.fetchall()
                cursor_g.close()
                
                # Map to products
                gallery_map = {pid: [] for pid in pids}
                for g in galleries:
                    gallery_map[g['product_id']].append(g['image_url'])
                    
                for p in products:
                    p['gallery'] = gallery_map.get(p['id'], [])
            
            import math
            return {
                "products": products,
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": math.ceil(total_count / limit)
            }
        except Exception as e:
            print(f"ERROR in list_products: {e}")
            raise HTTPException(500, f"DB Error: {str(e)}")
        finally:
            if conn.is_connected():
                conn.close()

    def update_product(self, product_id: int, data: ProductUpdate):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Check existence
            cursor.execute("SELECT id FROM products WHERE id=%s", (product_id,))
            if not cursor.fetchone():
                raise HTTPException(404, "Product not found")

            # Build dynamic update
            fields = []
            params = []
            
            # Helper to add fields
            def check_and_add(field_name, val):
                if val is not None:
                    fields.append(f"{field_name} = %s")
                    # Handle enum conversion
                    if isinstance(val, FulfillmentType):
                         params.append(val.value)
                    else:
                         params.append(val)

            check_and_add("name", data.name)
            check_and_add("description", data.description)
            check_and_add("price", data.price)
            check_and_add("discount_price", data.discount_price)
            check_and_add("stock_quantity", data.stock_quantity)
            check_and_add("category", data.category)
            check_and_add("fulfillment_type", data.fulfillment_type)
            check_and_add("video_url", data.video_url)
            check_and_add("is_active", data.is_active)
            
            if fields:
                sql = "UPDATE products SET " + ", ".join(fields) + " WHERE id = %s"
                params.append(product_id)
                cursor.execute(sql, params)
                
            # Update Gallery if provided (Replace all)
            if data.gallery is not None:
                cursor.execute("DELETE FROM product_gallery WHERE product_id=%s", (product_id,))
                if data.gallery:
                    gallery_sql = "INSERT INTO product_gallery (product_id, image_url) VALUES (%s, %s)"
                    for img in data.gallery:
                        cursor.execute(gallery_sql, (product_id, img))
            
            conn.commit()
            
            cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
            prod = cursor.fetchone()
            
            cursor.execute("SELECT image_url FROM product_gallery WHERE product_id=%s", (product_id,))
            prod['gallery'] = [row['image_url'] for row in cursor.fetchall()]
            return prod
        finally:
            cursor.close()
            conn.close()

    def delete_product(self, product_id: int): # Soft delete usually better
        return self.update_product(product_id, ProductUpdate(is_active=False))

    # --- CART ---
    def get_user_cart(self, user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Get or Create Cart
            cursor.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = cursor.fetchone()
            
            if not cart:
                cursor.execute("INSERT INTO carts (user_id) VALUES (%s)", (user_id,))
                conn.commit()
                cart_id = cursor.lastrowid
            else:
                cart_id = cart['id']
            
            # 2. Get Items
            sql = """
                SELECT ci.id, ci.product_id, ci.quantity, p.name as product_name, p.price, p.discount_price, p.image_url
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.cart_id = %s
            """
            cursor.execute(sql, (cart_id,))
            items = cursor.fetchall()
            
            # 3. Calculate Totals
            response_items = []
            cart_total = 0
            
            for item in items:
                # Use discount price if available
                final_price = item['discount_price'] if item['discount_price'] else item['price']
                total_item_price = float(final_price) * item['quantity']
                cart_total += total_item_price
                
                response_items.append({
                    "id": item['id'],
                    "product_id": item['product_id'],
                    "product_name": item['product_name'],
                    "price": float(final_price),
                    "image_url": item['image_url'],
                    "quantity": item['quantity'],
                    "total_price": total_item_price
                })
                
            return {
                "id": cart_id,
                "user_id": user_id,
                "items": response_items,
                "cart_total": cart_total
            }
        finally:
            cursor.close()
            conn.close()

    def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Ensure Product exists and has stock
            cursor.execute("SELECT id, stock_quantity FROM products WHERE id=%s AND is_active=1", (product_id,))
            prod = cursor.fetchone()
            if not prod:
                raise HTTPException(404, "Product not found")
            if prod['stock_quantity'] < quantity:
                raise HTTPException(400, "Insufficient stock")

            # Get Cart ID (Reusing logic logic or fetching directly)
            cursor.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = cursor.fetchone()
            if not cart:
                cursor.execute("INSERT INTO carts (user_id) VALUES (%s)", (user_id,))
                conn.commit()
                cart_id = cursor.lastrowid
            else:
                cart_id = cart['id']

            # Insert or Update Item
            sql = """
                INSERT INTO cart_items (cart_id, product_id, quantity) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """
            cursor.execute(sql, (cart_id, product_id, quantity))
            conn.commit()
            
            return self.get_user_cart(user_id)
        finally:
            cursor.close()
            conn.close()
            
    def remove_from_cart(self, user_id: int, item_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
             # Verify ownership via join
             cursor.execute("""
                DELETE ci FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.id
                WHERE ci.id = %s AND c.user_id = %s
             """, (item_id, user_id))
             conn.commit()
             return self.get_user_cart(user_id)
        finally:
             cursor.close()
             conn.close()

    # --- ORDERS ---
    def create_order(self, user_id: int, data: OrderCreate):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Get Cart
            cart = self.get_user_cart(user_id)
            if not cart['items']:
                raise HTTPException(400, "Cart is empty")

            # 2. Validate Stock again (Race condition check)
            # For simplicity, we assume stock is fine or fail insert if we had DB constraints (we check individually)
            
            # 3. Create Order
            sql = """
                INSERT INTO shop_orders (user_id, total_amount, order_status, payment_status, delivery_method, shipping_address)
                VALUES (%s, %s, 'pending', 'pending', %s, %s)
            """
            cursor.execute(sql, (user_id, cart['cart_total'], data.delivery_method.value, data.shipping_address))
            order_id = cursor.lastrowid
            
            # 4. Move items to Order Items
            item_sql = """
                INSERT INTO shop_order_items (order_id, product_id, quantity, price_at_purchase)
                VALUES (%s, %s, %s, %s)
            """
            for item in cart['items']:
                 cursor.execute(item_sql, (order_id, item['product_id'], item['quantity'], item['price']))
                 
                 # Deduct Stock ATOMICALLY (Optimistic Locking)
                 # returns 0 if WHERE condition fails (e.g., stock < quantity)
                 cursor.execute("""
                    UPDATE products 
                    SET stock_quantity = stock_quantity - %s 
                    WHERE id=%s AND stock_quantity >= %s AND is_active = 1
                 """, (item['quantity'], item['product_id'], item['quantity']))
                 
                 if cursor.rowcount == 0:
                     raise HTTPException(400, f"Product {item['product_name']} is unavailable or insufficient stock")
            
            # 5. Clear Cart
            cursor.execute("DELETE FROM cart_items WHERE cart_id=%s", (cart['id'],))
            
            conn.commit()
            return {"order_id": order_id, "message": "Order created successfully"}
            
        except Exception as e:
            conn.rollback()
            # Re-raise HTTP exceptions as-is
            if isinstance(e, HTTPException):
                raise e
            # Wrap DB/Runtime errors
            raise HTTPException(500, f"Order processing failed: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def get_orders(self, user_id: int = None, admin_view: bool = False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT id, user_id, total_amount, order_status, payment_status, delivery_method, tracking_number, created_at
                FROM shop_orders
            """
            params = []
            if not admin_view:
                sql += " WHERE user_id = %s"
                params.append(user_id)
            
            sql += " ORDER BY created_at DESC"
            
            cursor.execute(sql, params)
            orders = cursor.fetchall()
            
            # Fetch Items for each? Or lazily. Let's do a simple join or just return basic info list.
            # Usually better to have a separate detail view, but for MVP list:
            return orders
        finally:
            cursor.close()
            conn.close()
            
    def update_order_status(self, order_id: int, status: str, tracking: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            sql = "UPDATE shop_orders SET order_status=%s"
            params = [status]
            if tracking:
                 sql += ", tracking_number=%s"
                 params.append(tracking)
                 
            sql += " WHERE id=%s"
            params.append(order_id)
            
            cursor.execute(sql, params)
            conn.commit()
            return {"msg": "Status updated"}
        finally:
            if conn.is_connected():
                conn.close()

    def request_return(self, order_id: int, user_id: int, reason: str):
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Check order ownership and status
            cursor.execute("SELECT * FROM shop_orders WHERE id = %s AND user_id = %s", (order_id, user_id))
            order = cursor.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            if order['order_status'] != 'delivered':
                raise HTTPException(status_code=400, detail="Only delivered orders can be returned")
            
            # Check existing return
            if order.get('return_status') and order['return_status'] != 'none':
                 raise HTTPException(status_code=400, detail=f"Return already in status: {order['return_status']}")

            cursor.execute("UPDATE shop_orders SET return_status = 'requested', return_reason = %s WHERE id = %s", (reason, order_id))
            conn.commit()
            return {"message": "Return requested successfully"}
        finally:
            if conn.is_connected():
                conn.close()

    def process_return(self, order_id: int, status: str): # status: approved, rejected
        if status not in ['approved', 'rejected']:
             raise HTTPException(status_code=400, detail="Invalid return status")
             
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE shop_orders SET return_status = %s WHERE id = %s", (status, order_id))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Order not found")
            return {"message": f"Return {status}"}
        finally:
            if conn.is_connected():
                conn.close()

    def generate_invoice(self, order_id: int):
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Get Order + User
            cursor.execute("""
                SELECT o.*, u.full_name, u.email 
                FROM shop_orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.id = %s
            """, (order_id,))
            order = cursor.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Get Items
            cursor.execute("""
                SELECT oi.*, p.name 
                FROM shop_order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cursor.fetchall()
            
            # Simple HTML Invoice
            invoice_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h1>Invoice #{order['id']}</h1>
                <p><strong>Date:</strong> {order['created_at']}</p>
                <p><strong>Customer:</strong> {order['full_name']} ({order['email']})</p>
                <p><strong>Status:</strong> {order['order_status'].upper()}</p>
                <hr>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px; text-align: left;">Product</th>
                        <th style="padding: 8px; text-align: right;">Qty</th>
                        <th style="padding: 8px; text-align: right;">Price</th>
                        <th style="padding: 8px; text-align: right;">Total</th>
                    </tr>
            """
            
            total = 0
            for item in items:
                line_total = item['quantity'] * item['price_at_purchase']
                total += line_total
                invoice_html += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item['name']}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{item['quantity']}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item['price_at_purchase']}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${line_total}</td>
                    </tr>
                """
            
            invoice_html += f"""
                    <tr>
                        <td colspan="3" style="padding: 8px; text-align: right;"><strong>Grand Total:</strong></td>
                        <td style="padding: 8px; text-align: right;"><strong>${total}</strong></td>
                    </tr>
                </table>
                <br>
                <p>Thank you for shopping with SkinSage!</p>
            </body>
            </html>
            """
            return invoice_html
        finally:
            if conn.is_connected():
                conn.close()
