"""
Script để tạo tài khoản admin mặc định
"""
from app.database import SessionLocal, User
from passlib.context import CryptContext
import bcrypt

def get_password_hash(password: str) -> str:
    # Hash password với bcrypt trực tiếp
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

db = SessionLocal()

# Kiểm tra xem đã có admin chưa
admin = db.query(User).filter(User.email == "admin@bookstore.com").first()

if admin:
    print("✅ Tài khoản admin đã tồn tại!")
    print(f"   Email: {admin.email}")
    print(f"   Mật khẩu: admin123")
else:
    # Tạo admin mới
    admin = User(
        email="admin@bookstore.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Administrator",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("✅ Đã tạo tài khoản admin thành công!")
    print(f"   Email: admin@bookstore.com")
    print(f"   Mật khẩu: admin123")
    print("\n⚠️  Lưu ý: Vui lòng đổi mật khẩu sau khi đăng nhập!")

db.close()

