"""
Authentication cho SQLAdmin
"""
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.database import User, SessionLocal
import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        try:
            form = await request.form()
            # SQLAdmin có thể dùng "username" hoặc "email"
            email = form.get("email") or form.get("username")
            password = form.get("password")
            
            # Debug: in tất cả form keys
            print(f"Form keys: {list(form.keys()) if hasattr(form, 'keys') else 'N/A'}")
            print(f"Email from form: {email}")
            print(f"Password present: {bool(password)}")
        except Exception as e:
            print(f"Form parse error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        if not email or not password:
            print(f"Missing email or password: email={email}, password={'*' * len(password) if password else None}")
            return False
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                print(f"User not found: {email}")
                return False
            
            if not verify_password(password, user.hashed_password):
                print(f"Invalid password for: {email}")
                return False
            
            if user.role != "admin":
                print(f"User is not admin: {email}, role={user.role}")
                return False
            
            if not user.is_active:
                print(f"User is inactive: {email}")
                return False
            
            # Lưu thông tin vào session
            request.session.update({"admin_user_id": user.id, "admin_email": user.email})
            print(f"Admin login successful: {email}")
            return True
        except Exception as e:
            print(f"Admin login error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
    
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        admin_user_id = request.session.get("admin_user_id")
        if not admin_user_id:
            return False
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == admin_user_id).first()
            if not user or user.role != "admin" or not user.is_active:
                return False
            return True
        finally:
            db.close()

import os
authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))

