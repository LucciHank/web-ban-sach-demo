import sqlite3
import os

DB_FILE = "bookstore.db"

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found. Skipping migration.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(categories)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "image_url" not in columns:
            print("Adding image_url column to categories table...")
            cursor.execute("ALTER TABLE categories ADD COLUMN image_url TEXT DEFAULT NULL")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column image_url already exists.")
            
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
