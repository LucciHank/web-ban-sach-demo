from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Book, SessionLocal
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_cart(session_id: str, db: Session) -> Cart:
    """Lấy hoặc tạo giỏ hàng"""
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if not cart:
        cart = Cart(session_id=session_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

class CartItemRequest(BaseModel):
    book_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    book_id: int
    quantity: int
    book_title: str
    book_price: float
    book_image: Optional[str]
    subtotal: float
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    session_id: str
    items: List[CartItemResponse]
    total: float

@router.post("/add")
def add_to_cart(
    item: CartItemRequest,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Thêm sách vào giỏ hàng"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Kiểm tra sách tồn tại
    book = db.query(Book).filter(Book.id == item.book_id, Book.is_active == True).first()
    if not book:
        raise HTTPException(status_code=404, detail="Sách không tồn tại")
    
    if book.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Số lượng không đủ")
    
    # Lấy hoặc tạo giỏ hàng
    cart = get_or_create_cart(session_id, db)
    
    # Kiểm tra item đã có trong giỏ chưa
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.book_id == item.book_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item.quantity
        if existing_item.quantity > book.stock:
            raise HTTPException(status_code=400, detail="Số lượng vượt quá tồn kho")
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            book_id=item.book_id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    return {"message": "Đã thêm vào giỏ hàng", "session_id": session_id}

@router.get("/", response_model=CartResponse)
def get_cart(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Lấy giỏ hàng"""
    if not session_id:
        return CartResponse(id=0, session_id="", items=[], total=0.0)
    
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if not cart:
        return CartResponse(id=0, session_id=session_id, items=[], total=0.0)
    
    items = []
    total = 0.0
    
    for item in cart.items:
        book = item.book
        subtotal = book.price_vnd * item.quantity
        total += subtotal
        
        items.append(CartItemResponse(
            id=item.id,
            book_id=item.book_id,
            quantity=item.quantity,
            book_title=book.title,
            book_price=book.price_vnd,
            book_image=book.image_url,
            subtotal=subtotal
        ))
    
    return CartResponse(
        id=cart.id,
        session_id=cart.session_id,
        items=items,
        total=total
    )

@router.put("/item/{item_id}")
def update_cart_item(
    item_id: int,
    quantity: int,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Cập nhật số lượng item trong giỏ"""
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Giỏ hàng không tồn tại")
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item không tồn tại")
    
    if quantity <= 0:
        db.delete(cart_item)
    else:
        if cart_item.book.stock < quantity:
            raise HTTPException(status_code=400, detail="Số lượng không đủ")
        cart_item.quantity = quantity
    
    db.commit()
    return {"message": "Đã cập nhật"}

@router.delete("/item/{item_id}")
def remove_cart_item(item_id: int, session_id: str, db: Session = Depends(get_db)):
    """Xóa item khỏi giỏ hàng"""
    cart = db.query(Cart).filter(Cart.session_id == session_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Giỏ hàng không tồn tại")
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item không tồn tại")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Đã xóa"}

