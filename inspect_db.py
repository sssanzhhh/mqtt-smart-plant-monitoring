"""Quick utility to inspect recent rows in the SQLite database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DATABASE_PATH = "plant_monitoring.db"


def print_rows(cursor: sqlite3.Cursor, query: str, title: str) -> None:
    print(f"\n== {title} ==")
    rows = cursor.execute(query).fetchall()
    if not rows:
        print("(no rows)")
        return

    for row in rows:
        print(row)


def main() -> int:
    database_path = Path(DATABASE_PATH)
    if not database_path.exists():
        print(f"Database not found: {database_path}")
        return 1

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        print_rows(
            cursor,
            """
            SELECT id, timestamp, plant_id, soil_moisture, temperature, humidity
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 10
            """,
            "Latest Sensor Readings",
        )
        print_rows(
            cursor,
            """
            SELECT id, timestamp, event_type, details
            FROM activity_log
            ORDER BY id DESC
            LIMIT 20
            """,
            "Latest Activity",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
