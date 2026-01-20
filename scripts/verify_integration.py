import os
import json
import hmac
import hashlib
import time
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv("KLTN_WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("KLTN_WEBHOOK_SECRET")

print(f"--- Configuration ---")
print(f"URL: {WEBHOOK_URL}")
print(f"Secret: {WEBHOOK_SECRET[:6]}...{WEBHOOK_SECRET[-6:] if WEBHOOK_SECRET else ''}")
print("---------------------")

if not WEBHOOK_URL or not WEBHOOK_SECRET:
    print("❌ Missing WEBHOOK_URL or KLTN_WEBHOOK_SECRET in .env")
    exit(1)

def generate_signature(payload_str):
    return hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

def send_event(event_type, event_id, payload):
    payload_str = json.dumps(payload)
    signature = generate_signature(payload_str)
    
    headers = {
        "Content-Type": "application/json",
        "X-Event-Id": event_id,
        "X-Event-Type": event_type,
        "X-Signature": signature
    }
    
    print(f"\n🚀 Sending {event_type} [EventID: {event_id}]...")
    # print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = httpx.post(WEBHOOK_URL, content=payload_str, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Success")
        else:
            print("❌ Failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Product Data "Rich Dad Poor Dad"
product_data = {
    "products": [{
        "book_id": "FN001",
        "title": "Rich Dad Poor Dad",
        "authors": "Robert Kiyosaki",
        "price_vnd": 156000,
        "stock": 39,
        "is_active": True,
        "description": "Robert Kiyosaki chia sẻ những bài học tài chính đối lập...",
        "image_url": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1757619021i/69571.jpg"
    }],
    "action": "create" # This is inside the payload structure used in app/admin/config.py
}

# The user's guide mentions simplified body for direct webhook, 
# BUT the app/admin/config.py sends { "action": ..., "products": [...] }
# Let's match what the app actually sends (based on Step 238 code view)
# app/admin/config.py: 
# payload = { "action": action, "products": [...] }

# 1. TEST CREATE (UPSERT)
# Note: The KLTN docs likely map "create"/"update" actions to "product.upsert" event type
send_event(
    event_type="product.upsert",
    event_id=f"evt_{int(time.time())}_1",
    payload={
        "action": "create",
        "products": [{
            "book_id": "FN001",
            "title": "Rich Dad Poor Dad",
            "authors": "Robert Kiyosaki",
            "price_vnd": 156000,
            "stock": 39,
            "is_active": True,
            "description": "Robert Kiyosaki chia sẻ những bài học tài chính...",
            "image_url": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1757619021i/69571.jpg"
        }]
    }
)

time.sleep(2)

# 2. TEST UPDATE (Change Price & Stock)
send_event(
    event_type="product.upsert",
    event_id=f"evt_{int(time.time())}_2",
    payload={
        "action": "update",
        "products": [{
            "book_id": "FN001",
            "title": "Rich Dad Poor Dad (Updated Price)",
            "authors": "Robert Kiyosaki",
            "price_vnd": 199000, # Changed from 156000
            "stock": 45,       # Changed from 39
            "is_active": True,
             "image_url": "https://m.media-amazon.com/images/S/compressed.photo.goodreads.com/books/1757619021i/69571.jpg"
        }]
    }
)

time.sleep(2)

# 3. TEST DELETE
send_event(
    event_type="product.delete",
    event_id=f"evt_{int(time.time())}_3",
    payload={
        "action": "delete",
        "products": [{
            "book_id": "FN001"
        }]
    }
)
