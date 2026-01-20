# Hướng dẫn tích hợp KLTN Chatbot

Tài liệu này mô tả cách tích hợp Chatbot AI với website bán sách.

---

## 1. Thông tin cấu hình

| Thông số | Giá trị |
|----------|---------|
| **Shop ID** | `shop_test_2` |
| **API Base URL** | `https://unburst-ambroise-hydrorhizal.ngrok-free.dev` |
| **API Key** | `sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c` |
| **Webhook URL** | `https://unburst-ambroise-hydrorhizal.ngrok-free.dev/api/integrations/webhook/shop_test_2` |
| **Webhook Secret** | `whsec_ce81baafbb2ccc1d6d1b5498abeb48adfdf4d3170e805376` |

---

## 2. Nhúng Chat Widget vào Website

Thêm đoạn code sau vào trước thẻ `</body>` trong HTML:

```html
<!-- KLTN Chatbot Widget -->
<script>
  window.KLTN_SHOP_ID = "shop_test_2";
  window.KLTN_API_BASE = "https://unburst-ambroise-hydrorhizal.ngrok-free.dev";
  window.KLTN_API_KEY = "sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c";
</script>
<script src="https://unburst-ambroise-hydrorhizal.ngrok-free.dev/static/chat-widget.js"></script>
```

### Hoặc dùng iframe:

```html
<iframe 
  src="https://unburst-ambroise-hydrorhizal.ngrok-free.dev/embed/shop_test_2" 
  style="position:fixed;bottom:24px;right:24px;width:400px;height:550px;border:none;border-radius:20px;box-shadow:0 8px 40px rgba(0,0,0,0.15);z-index:9999">
</iframe>
```

---

## 3. Webhook - Đồng bộ sản phẩm

Khi thêm/sửa/xóa sản phẩm trong Admin, hệ thống tự động gửi webhook đến Chatbot API.

### 3.1. Cấu hình trong `.env`

```env
KLTN_WEBHOOK_URL=https://unburst-ambroise-hydrorhizal.ngrok-free.dev/api/integrations/webhook/shop_test_2
KLTN_WEBHOOK_SECRET=whsec_ce81baafbb2ccc1d6d1b5498abeb48adfdf4d3170e805376
```

### 3.2. Cách tạo chữ ký HMAC (X-Signature)

```python
import hmac
import hashlib
import json

# Payload JSON
payload = {
    "action": "create",  # hoặc "update", "delete"
    "products": [{
        "book_id": "123",
        "title": "Tên sách",
        "authors": "Tác giả",
        "price_vnd": 150000,
        "stock": 10,
        "is_active": True
    }]
}

# Chuyển thành bytes
body_bytes = json.dumps(payload).encode('utf-8')

# Tạo chữ ký
secret = "whsec_ce81baafbb2ccc1d6d1b5498abeb48adfdf4d3170e805376"
signature = hmac.new(
    secret.encode(),
    body_bytes,
    hashlib.sha256
).hexdigest()

# Gửi request với header
headers = {
    "Content-Type": "application/json",
    "X-Signature": signature
}
```

### 3.3. Payload mẫu

**Tạo mới sản phẩm:**
```json
{
  "action": "create",
  "products": [{
    "book_id": "1",
    "title": "Tư duy nhanh và chậm",
    "authors": "Daniel Kahneman",
    "price_vnd": 190000,
    "stock": 12,
    "is_active": true
  }]
}
```

**Cập nhật sản phẩm:**
```json
{
  "action": "update",
  "products": [{
    "book_id": "1",
    "title": "Tư duy nhanh và chậm (Bìa cứng)",
    "price_vnd": 250000,
    "stock": 8
  }]
}
```

**Xóa sản phẩm:**
```json
{
  "action": "delete",
  "products": [{
    "book_id": "1"
  }]
}
```

---

## 4. REST API Endpoints

### 4.1. Chat API

```
POST /api/chat_orchestrator
Authorization: Bearer sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c
Content-Type: application/json

{
  "shop_id": "shop_test_2",
  "user_id": "customer_123",
  "session_id": "sess_abc",
  "message": "Tôi muốn tìm sách self-help"
}
```

### 4.2. Widget Config

```
GET /api/widget/config/shop_test_2
Authorization: Bearer sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c
```

### 4.3. Danh sách sản phẩm

```
GET /api/shops/shop_test_2/products
Authorization: Bearer sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c
```

### 4.4. Lịch sử chat

```
GET /api/shops/shop_test_2/conversations
Authorization: Bearer sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c
```

---

## 5. Import sản phẩm từ Excel

### 5.1. Truy cập trang Import

```
http://localhost:8003/admin/import-products
```

### 5.2. Cấu trúc file Excel (.xlsx)

| Cột | Mô tả | Bắt buộc |
|-----|-------|----------|
| `title` | Tên sách | ✅ |
| `authors` | Tác giả | ✅ |
| `price_vnd` | Giá (VNĐ) | ✅ |
| `stock` | Tồn kho | |
| `genres_primary` | Thể loại chính | |
| `short_summary` | Mô tả ngắn | |
| `pages` | Số trang | |
| `year` | Năm xuất bản | |
| `publisher` | Nhà xuất bản | |
| `rating_avg` | Đánh giá TB | |
| `image_url` | URL ảnh | |

---

## 6. Kiểm tra kết nối

### Test Webhook:

```bash
curl -X POST "https://unburst-ambroise-hydrorhizal.ngrok-free.dev/api/integrations/webhook/shop_test_2" \
  -H "Content-Type: application/json" \
  -H "X-Signature: <hmac_signature>" \
  -d '{"action":"create","products":[{"book_id":"test","title":"Test Book"}]}'
```

### Test Chat API:

```bash
curl -X POST "https://unburst-ambroise-hydrorhizal.ngrok-free.dev/api/chat_orchestrator" \
  -H "Authorization: Bearer sk_tcCWyHBry9SPxo3WpqsFV1VYMHA3LH9aCeC8TIVHH8c" \
  -H "Content-Type: application/json" \
  -d '{"shop_id":"shop_test_2","user_id":"test","session_id":"test","message":"Xin chào"}'
```

---

## 7. Troubleshooting

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `401 Unauthorized` | API Key sai | Kiểm tra lại API Key |
| `403 Forbidden` | Signature sai | Kiểm tra lại HMAC secret |
| `404 Not Found` | Shop ID không tồn tại | Kiểm tra Shop ID |
| Widget không hiện | Script blocked | Kiểm tra CORS hoặc CSP |

---
