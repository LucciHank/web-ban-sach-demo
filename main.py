from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqladmin import Admin
from app.database import engine, Base
from app.admin.config import setup_admin
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Tạo database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trạm Sách", description="Cửa hàng sách trực tuyến - Apple style")

# Mount static files và templates
app.mount("/static", StaticFiles(directory="static"), name="static")
jinja_env = Environment(loader=FileSystemLoader("templates"))

# Setup admin panel với authentication
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))

from app.admin.auth import authentication_backend
print("--- Admin Template Dir:", os.path.join(os.path.dirname(__file__), "templates"))
admin = Admin(app, engine, authentication_backend=authentication_backend, templates_dir=os.path.join(os.path.dirname(__file__), "templates"))
setup_admin(admin)

# Import routers
from app.routers import products, cart, checkout, search, auth, orders

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(checkout.router, prefix="/api/checkout", tags=["checkout"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

def render_template(template_name: str, **kwargs):
    """Helper function to render Jinja2 templates"""
    template = jinja_env.get_template(template_name)
    return HTMLResponse(content=template.render(**kwargs))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ"""
    return render_template("index.html", request=request)

@app.get("/category/{category_slug}", response_class=HTMLResponse)
async def category_page(request: Request, category_slug: str):
    """Trang danh mục"""
    return render_template("category.html", request=request, category_slug=category_slug)

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int):
    """Trang chi tiết sản phẩm"""
    return render_template("product.html", request=request, product_id=product_id)

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    """Trang giỏ hàng"""
    return render_template("cart.html", request=request)

@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request):
    """Trang thanh toán"""
    return render_template("checkout.html", request=request)

@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    """Trang đặt hàng thành công"""
    return render_template("success.html", request=request)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Trang đăng nhập"""
    return render_template("user_login.html", request=request)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Trang đăng ký"""
    return render_template("register.html", request=request)

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Trang tài khoản"""
    return render_template("profile.html", request=request)

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    """Trang danh sách đơn hàng"""
    return render_template("orders.html", request=request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)

