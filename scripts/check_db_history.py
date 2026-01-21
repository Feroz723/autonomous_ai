import sqlite3
import os

db_path = "data/solopreneur.db"

def query_db():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("--- Tables ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(t[0])
            
        for table in ['posted_content', 'generated_content', 'system_logs']:
            print(f"\n--- Recent items from '{table}' ---")
            try:
                cursor.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 100;")
                rows = cursor.fetchall()
                for r in rows:
                    # Explicitly handle encoding for Windows console
                    line = str(r).encode('ascii', 'ignore').decode('ascii')
                    print(line)
            except Exception as e:
                print(f"Query error: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    query_db()
