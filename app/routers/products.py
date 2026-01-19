from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Book, Category, SessionLocal
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
    category_name: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[BookResponse])
def get_products(
    category_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lấy danh sách sách"""
    query = db.query(Book).filter(Book.is_active == True)
    
    if category_id:
        query = query.filter(Book.category_id == category_id)
    
    books = query.offset(offset).limit(limit).all()
    
    result = []
    for book in books:
        book_dict = BookResponse.model_validate(book).model_dump()
        if book.category:
            book_dict["category_name"] = book.category.name
        result.append(book_dict)
    
    return result

@router.get("/{book_id}", response_model=BookResponse)
def get_product(book_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết sách"""
    book = db.query(Book).filter(Book.id == book_id, Book.is_active == True).first()
    if not book:
        raise HTTPException(status_code=404, detail="Sách không tồn tại")
    
    result = BookResponse.model_validate(book).model_dump()
    if book.category:
        result["category_name"] = book.category.name
    return result

@router.get("/categories/all", response_model=List[dict])
def get_categories(db: Session = Depends(get_db)):
    """Lấy tất cả danh mục"""
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories]

@router.get("/categories/by-slug/{slug}", response_model=dict)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    """Lấy danh mục theo slug"""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Danh mục không tồn tại")
    return {"id": category.id, "name": category.name, "slug": category.slug}

