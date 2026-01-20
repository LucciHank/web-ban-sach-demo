from sqladmin import ModelView, BaseView, expose
from app.database import Book, Category, Order, OrderItem, Cart, CartItem, User
import httpx
import hmac
import hashlib
import json
import asyncio
import os
from datetime import datetime

# Webhook Configuration from environment variables
WEBHOOK_URL = os.getenv("KLTN_WEBHOOK_URL", "http://localhost:8000/api/integrations/webhook/shop_books_1")
WEBHOOK_SECRET = os.getenv("KLTN_WEBHOOK_SECRET", "whsec_3b21d0581774c56e6e92e560dd031b7a44a6c07da233e549")

class ImportProductsView(BaseView):
    name = "Import Excel"
    icon = "fa-solid fa-file-import"
    path = "/import-products"
    
    @expose("/import-products", methods=["GET"])
    async def import_page(self, request):
        return await self.templates.TemplateResponse(request, "admin/import_products.html")

import uuid

async def send_webhook(action: str, product: Book):
    """Send webhook to Chatbot API"""
    try:
        # Determine event type
        event_type = "product.upsert" if action in ["create", "update"] else "product.delete"
        
        # 1. Prepare payload
        payload = {
            "action": action, # Keep backward compatibility
            "products": [{
                "book_id": str(product.id),
                "title": product.title,
                "authors": product.authors,
                "price_vnd": float(product.price_vnd) if product.price_vnd else 0,
                "stock": int(product.stock) if product.stock else 0,
                "is_active": product.is_active,
                "image_url": product.image_url,
                "description": product.description
            }]
        }
        # Use ensure_ascii=False to support Vietnamese characters in JSON, matching common payload standards
        json_payload = json.dumps(payload, ensure_ascii=False)
        
        # Generate Event ID
        event_id = str(uuid.uuid4())

        # Debug Secret (Masked)
        masked_secret = f"{WEBHOOK_SECRET[:5]}...{WEBHOOK_SECRET[-5:]}" if WEBHOOK_SECRET else "None"
        print(f"--- DEBUG: Using Secret: {masked_secret}")

        # 2. Calculate Signature
        signature = hmac.new(
            WEBHOOK_SECRET.encode(),
            json_payload.encode(), # Encode to UTF-8 bytes
            hashlib.sha256
        ).hexdigest()

        # Debug Logs
        print(f"\n--- WEBHOOK OUTBOUND ---")
        print(f"URL: {WEBHOOK_URL}")
        print(f"EVENT_ID: {event_id} | TYPE: {event_type}")
        print(f"PAYLOAD (Raw): {json_payload}") # Print raw string to verify encoding

        
        # 3. Send Request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WEBHOOK_URL,
                content=json_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": signature,
                    "X-Event-Id": event_id,
                    "X-Event-Type": event_type
                },
                timeout=10.0
            )
            print(f"--- RESPONSE: {response.status_code} {response.text}")
            print(f"------------------------\n")

    except Exception as e:
        print(f"!!! Webhook Error: {e}")




def setup_admin(admin):
    """Setup admin views"""
    
    class BookAdmin(ModelView, model=Book):
        can_export = False  # Disable export, use Import from sidebar instead
        column_list = [Book.id, Book.title, Book.authors, Book.price_vnd, Book.stock, Book.is_active]
        column_searchable_list = [Book.title, Book.authors]
        column_sortable_list = [Book.price_vnd, Book.stock, Book.created_at]
        form_columns = [
            "title", "authors", "description", "price_vnd", "stock", 
            "image_url", "rating_avg", "pages", "publisher", "publish_year", 
            "is_active", "category_id"
        ]
        name = "Sách"
        name_plural = "Sách"
        icon = "fa-solid fa-book"

        async def after_model_change(self, data, model, is_created, request):
            action = "create" if is_created else "update"
            await send_webhook(action, model)

        async def after_model_delete(self, model, request):
            await send_webhook("delete", model)

    
    class CategoryAdmin(ModelView, model=Category):
        column_list = [Category.id, Category.name, Category.slug, Category.image_url]
        column_searchable_list = [Category.name]
        form_columns = ["name", "slug", "description", "image_url"]
        name = "Danh mục"
        name_plural = "Danh mục"
        icon = "fa-solid fa-folder"
    
    class OrderAdmin(ModelView, model=Order):
        column_list = [
            Order.id, Order.order_number, Order.customer_name, 
            Order.customer_phone, Order.total, Order.status, Order.created_at
        ]
        column_searchable_list = [Order.order_number, Order.customer_name, Order.customer_phone]
        column_sortable_list = [Order.created_at, Order.total]
        name = "Đơn hàng"
        name_plural = "Đơn hàng"
        icon = "fa-solid fa-shopping-bag"
    
    class OrderItemAdmin(ModelView, model=OrderItem):
        column_list = [OrderItem.id, OrderItem.order_id, OrderItem.book_id, OrderItem.quantity, OrderItem.price_vnd]
        name = "Chi tiết đơn hàng"
        name_plural = "Chi tiết đơn hàng"
        icon = "fa-solid fa-list"
    
    class CartAdmin(ModelView, model=Cart):
        column_list = [Cart.id, Cart.session_id, Cart.created_at, Cart.updated_at]
        name = "Giỏ hàng"
        name_plural = "Giỏ hàng"
        icon = "fa-solid fa-cart-shopping"
    
    class UserAdmin(ModelView, model=User):
        column_list = [User.id, User.email, User.full_name, User.role, User.is_active, User.created_at]
        column_searchable_list = [User.email, User.full_name]
        column_sortable_list = [User.created_at, User.role]
        form_columns = ["email", "full_name", "phone", "role", "is_active"]
        name = "Người dùng"
        name_plural = "Người dùng"
        icon = "fa-solid fa-user"
    
    admin.add_view(BookAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(OrderItemAdmin)
    admin.add_view(CartAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(ImportProductsView)

