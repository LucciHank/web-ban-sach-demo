from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Cart, Order, OrderItem, Book, SessionLocal
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random
import string

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CheckoutRequest(BaseModel):
    session_id: str
    customer_name: str
    customer_phone: str
    customer_address: str
    shipping_method: str = "standard"
    payment_method: str = "cod"
    user_id: Optional[int] = None

class OrderResponse(BaseModel):
    order_id: int
    order_number: str
    total: float
    customer_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

def generate_order_number() -> str:
    """Tạo mã đơn hàng"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{timestamp}-{random_str}"

@router.post("/", response_model=OrderResponse)
def create_order(checkout_data: CheckoutRequest, db: Session = Depends(get_db)):
    """Tạo đơn hàng"""
    # Lấy giỏ hàng
    cart = db.query(Cart).filter(Cart.session_id == checkout_data.session_id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Giỏ hàng trống")
    
    # Kiểm tra tồn kho và tính tổng
    total = 0.0
    order_items_data = []
    
    for item in cart.items:
        book = item.book
        if book.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Sách '{book.title}' không đủ số lượng"
            )
        
        subtotal = book.price_vnd * item.quantity
        total += subtotal
        
        order_items_data.append({
            "book_id": book.id,
            "quantity": item.quantity,
            "price_vnd": book.price_vnd
        })
    
    # Tạo đơn hàng
    order = Order(
        order_number=generate_order_number(),
        session_id=checkout_data.session_id,
        user_id=checkout_data.user_id,
        customer_name=checkout_data.customer_name,
        customer_phone=checkout_data.customer_phone,
        customer_address=checkout_data.customer_address,
        shipping_method=checkout_data.shipping_method,
        payment_method=checkout_data.payment_method,
        total=total,
        status="pending"
    )
    db.add(order)
    db.flush()
    
    # Tạo order items và giảm tồn kho
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            book_id=item_data["book_id"],
            quantity=item_data["quantity"],
            price_vnd=item_data["price_vnd"]
        )
        db.add(order_item)
        
        # Giảm tồn kho
        book = db.query(Book).filter(Book.id == item_data["book_id"]).first()
        book.stock -= item_data["quantity"]
    
    # Xóa giỏ hàng
    db.delete(cart)
    
    db.commit()
    db.refresh(order)
    
    return OrderResponse(
        order_id=order.id,
        order_number=order.order_number,
        total=order.total,
        customer_name=order.customer_name,
        created_at=order.created_at
    )

@router.get("/order/{order_number}", response_model=OrderResponse)
def get_order(order_number: str, db: Session = Depends(get_db)):
    """Lấy thông tin đơn hàng"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
    
    return OrderResponse(
        order_id=order.id,
        order_number=order.order_number,
        total=order.total,
        customer_name=order.customer_name,
        created_at=order.created_at
    )

