"""Validate required runtime directories, files, and SQLite access."""

import json
import os
import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = (
    "data/trend_plans",
    "data/analytics",
    "products",
    "landing",
    "docs",
)
REQUIRED_FILES = ("data/content_queue.json",)
DB_PATH = "data/solopreneur.db"


def project_path(path: str) -> Path:
    return PROJECT_ROOT / path


def check_dirs() -> bool:
    for relative_path in REQUIRED_DIRS:
        path = project_path(relative_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"DIR_OK: {relative_path}")
        except OSError as exc:
            print(f"DIR_ERROR: {relative_path}: {exc}")
            return False
    return True


def check_files() -> bool:
    valid = True
    for relative_path in REQUIRED_FILES:
        path = project_path(relative_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("[]", encoding="utf-8")
                print(f"FILE_CREATED: {relative_path}")
            else:
                with path.open("r", encoding="utf-8") as queue_file:
                    json.load(queue_file)
                print(f"FILE_OK: {relative_path}")
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FILE_ERROR: {relative_path}: {exc}")
            valid = False
    return valid


def check_db() -> bool:
    db_path = project_path(DB_PATH)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as conn:
            conn.execute("SELECT 1")
        print("DB_OK")
        return True
    except sqlite3.Error as exc:
        print(f"DB_ERROR: {exc}")
        return False


def main() -> int:
    checks = (check_dirs(), check_files(), check_db())
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
