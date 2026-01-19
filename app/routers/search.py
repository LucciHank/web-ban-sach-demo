from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Book, SessionLocal
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookResponse(BaseModel):
    id: int
    title: str
    authors: str
    description: Optional[str]
    price_vnd: float
    stock: int
    image_url: Optional[str]
    rating_avg: float
    pages: Optional[int]
    publisher: Optional[str]
    publish_year: Optional[int]
    category_id: Optional[int]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=dict)
def search_books(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    category_id: Optional[int] = Query(None, description="Danh mục"),
    price_min: Optional[float] = Query(None, description="Giá tối thiểu"),
    price_max: Optional[float] = Query(None, description="Giá tối đa"),
    author: Optional[str] = Query(None, description="Tác giả"),
    sort_by: Optional[str] = Query("newest", description="Sắp xếp: newest, price_asc, price_desc, rating"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Tìm kiếm và lọc sách"""
    query = db.query(Book).filter(Book.is_active == True)
    
    # Tìm kiếm theo từ khóa
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Book.title.ilike(search_term),
                Book.authors.ilike(search_term),
                Book.description.ilike(search_term)
            )
        )
    
    # Lọc theo danh mục
    if category_id:
        query = query.filter(Book.category_id == category_id)
    
    # Lọc theo giá
    if price_min is not None:
        query = query.filter(Book.price_vnd >= price_min)
    if price_max is not None:
        query = query.filter(Book.price_vnd <= price_max)
    
    # Lọc theo tác giả
    if author:
        query = query.filter(Book.authors.ilike(f"%{author}%"))
    
    # Sắp xếp
    if sort_by == "price_asc":
        query = query.order_by(Book.price_vnd.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Book.price_vnd.desc())
    elif sort_by == "rating":
        query = query.order_by(Book.rating_avg.desc())
    else:  # newest
        query = query.order_by(Book.created_at.desc())
    
    # Đếm tổng số
    total = query.count()
    
    # Lấy kết quả
    books = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "books": [BookResponse.model_validate(book).model_dump() for book in books]
    }

