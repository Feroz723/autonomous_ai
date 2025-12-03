import os
import sqlite3

REQUIRED_DIRS = [
    "data/trend_plans",
    "data/analytics",
    "products",
    "landing",
    "docs"
]

REQUIRED_FILES = [
    "data/content_queue.json"
]

DB_PATH = "data/solopreneur.db"

def check_dirs():
    for d in REQUIRED_DIRS:
        os.makedirs(d, exist_ok=True)
        print(f"DIR_OK: {d}")

def check_files():
    for f in REQUIRED_FILES:
        if not os.path.exists(f):
            with open(f, 'w') as fp:
                fp.write("[]")
            print(f"FILE_CREATED: {f}")
        else:
            print(f"FILE_OK: {f}")

def check_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        print("DB_OK")
    except Exception as e:
        print(f"DB_ERROR: {e}")

if __name__ == "__main__":
    check_dirs()
    check_files()
    check_db()
