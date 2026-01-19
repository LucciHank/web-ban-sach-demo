# Hướng dẫn chạy nhanh

## Bước 1: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## Bước 2: Seed dữ liệu mẫu

```bash
python seed_data.py
```

Sẽ tạo:
- 5 danh mục sách
- 10 cuốn sách mẫu

## Bước 3: Chạy server

```bash
python main.py
```

Hoặc:

```bash
uvicorn main:app --reload
```

## Bước 4: Truy cập

- **Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## Kiểm tra nhanh

1. Vào trang chủ → Xem sách nổi bật
2. Click "Tất cả sách" → Tìm kiếm và lọc sách
3. Click vào 1 cuốn sách → Xem chi tiết
4. Click "Thêm vào giỏ hàng"
5. Vào giỏ hàng → Thanh toán
6. Điền form → Đặt hàng
7. Xem trang thành công

## Admin Panel

Truy cập `/admin` để:
- Quản lý sách (thêm, sửa, xóa)
- Quản lý danh mục
- Xem đơn hàng
- Xem giỏ hàng

## Lưu ý

- Database SQLite tự động tạo tại `bookstore.db`
- Cart sử dụng session_id lưu trong localStorage
- Không cần đăng nhập cho demo

