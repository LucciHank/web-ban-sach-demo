"""
Migration script to fix SQLite database constraints.
Run this script to update the database schema to allow book deletion.
"""
import sqlite3
import os

DB_PATH = "bookstore.db"
BACKUP_PATH = "bookstore_backup.db"

def migrate_database():
    """Fix foreign key constraints for order_items and cart_items"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found!")
        return False
    
    # Create backup
    import shutil
    shutil.copy(DB_PATH, BACKUP_PATH)
    print(f"✓ Created backup: {BACKUP_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # === Fix cart_items table ===
        print("\n--- Migrating cart_items table ---")
        
        # Create new table with correct constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_items_new (
                id INTEGER PRIMARY KEY,
                cart_id INTEGER NOT NULL,
                book_id INTEGER,
                quantity INTEGER DEFAULT 1 NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cart_id) REFERENCES carts(id),
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
            )
        """)
        
        # Copy data
        cursor.execute("""
            INSERT INTO cart_items_new (id, cart_id, book_id, quantity, created_at)
            SELECT id, cart_id, book_id, quantity, created_at FROM cart_items
        """)
        
        # Drop old and rename new
        cursor.execute("DROP TABLE cart_items")
        cursor.execute("ALTER TABLE cart_items_new RENAME TO cart_items")
        print("✓ cart_items migrated")
        
        # === Fix order_items table ===
        print("\n--- Migrating order_items table ---")
        
        # Create new table with correct constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items_new (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                book_id INTEGER,
                quantity INTEGER NOT NULL,
                price_vnd REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
            )
        """)
        
        # Copy data
        cursor.execute("""
            INSERT INTO order_items_new (id, order_id, book_id, quantity, price_vnd, created_at)
            SELECT id, order_id, book_id, quantity, price_vnd, created_at FROM order_items
        """)
        
        # Drop old and rename new
        cursor.execute("DROP TABLE order_items")
        cursor.execute("ALTER TABLE order_items_new RENAME TO order_items")
        print("✓ order_items migrated")
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("You can now delete books without getting constraint errors.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        print(f"Restoring from backup...")
        shutil.copy(BACKUP_PATH, DB_PATH)
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
