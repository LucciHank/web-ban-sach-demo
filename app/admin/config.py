from sqladmin import ModelView
from app.database import Book, Category, Order, OrderItem, Cart, CartItem, User

def setup_admin(admin):
    """Setup admin views"""
    
    class BookAdmin(ModelView, model=Book):
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

