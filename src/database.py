
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("data/processed/warehouse_inspections.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT NOT NULL,
                object_count INTEGER DEFAULT 0,
                text_region_count INTEGER DEFAULT 0,
                inspection_data TEXT NOT NULL,
                ai_analysis TEXT,
                created_at TEXT NOT NULL
            )
        """)


def save_inspection(inspection, ai_analysis=None):
    initialize_database()

    object_count = inspection["object_detection"]["total_objects"]
    text_count = inspection["ocr"]["total_text_regions"]

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO inspections (
                image_name,
                object_count,
                text_region_count,
                inspection_data,
                ai_analysis,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            inspection["image"],
            object_count,
            text_count,
            json.dumps(inspection),
            json.dumps(ai_analysis) if ai_analysis else None,
            datetime.now(timezone.utc).isoformat()
        ))

        return cursor.lastrowid


def get_inspections(limit=50):
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, image_name, object_count,
                   text_region_count, created_at
            FROM inspections
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [dict(row) for row in rows]


def get_inspection_by_id(inspection_id):
    initialize_database()

    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM inspections
            WHERE id = ?
        """, (inspection_id,)).fetchone()

        if row is None:
            return None

        result = dict(row)
        result["inspection_data"] = json.loads(
            result["inspection_data"]
        )

        if result["ai_analysis"]:
            result["ai_analysis"] = json.loads(
                result["ai_analysis"]
            )

        return result
