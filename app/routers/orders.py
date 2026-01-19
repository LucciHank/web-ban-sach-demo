from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Order, OrderItem, SessionLocal
from app.routers.auth import get_current_active_user
from app.database import User
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OrderItemResponse(BaseModel):
    id: int
    book_id: int
    book_title: str
    quantity: int
    price_vnd: float
    subtotal: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_phone: str
    customer_address: str
    shipping_method: str
    payment_method: str
    total: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách đơn hàng của user hiện tại"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    
    result = []
    for order in orders:
        items = []
        for item in order.items:
            items.append(OrderItemResponse(
                id=item.id,
                book_id=item.book_id,
                book_title=item.book.title,
                quantity=item.quantity,
                price_vnd=item.price_vnd,
                subtotal=item.price_vnd * item.quantity
            ))
        
        result.append(OrderResponse(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            shipping_method=order.shipping_method,
            payment_method=order.payment_method,
            total=order.total,
            status=order.status,
            created_at=order.created_at,
            items=items
        ))
    
    return result

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lấy chi tiết đơn hàng"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
    
    items = []
    for item in order.items:
        items.append(OrderItemResponse(
            id=item.id,
            book_id=item.book_id,
            book_title=item.book.title,
            quantity=item.quantity,
            price_vnd=item.price_vnd,
            subtotal=item.price_vnd * item.quantity
        ))
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        shipping_method=order.shipping_method,
        payment_method=order.payment_method,
        total=order.total,
        status=order.status,
        created_at=order.created_at,
        items=items
    )

