"""Quick utility to inspect recent rows in the SQLite database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

# Path to the database file — must match the value in config.py
DATABASE_PATH = "plant_monitoring.db"

SENSOR_COLUMNS = [
    "id",
    "timestamp",
    "plant_id",
    "plant_type",
    "soil_moisture",
    "temperature",
    "humidity",
    "nitrogen",
    "phosphorus",
    "potassium",
    "soil_ph",
    "salinity",
    "root_temperature",
]

ACTIVITY_COLUMNS = [
    "id",
    "timestamp",
    "plant_id",
    "plant_type",
    "event_type",
    "severity",
    "details",
]


def table_columns(cursor: sqlite3.Cursor, table_name: str) -> set[str]:
    rows = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def print_rows(cursor: sqlite3.Cursor, query: str, title: str) -> None:
    """Execute a query and print results with a header and column names."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")

    rows = cursor.execute(query).fetchall()

    if not rows:
        print("  (no rows)")
        return

    # Extract column names from the cursor description after executing the query
    col_names = [desc[0] for desc in cursor.description]
    print("  " + "  |  ".join(col_names))
    print("  " + "─" * (len("  |  ".join(col_names)) + 2))

    # Print each row, replacing None values with a dash for readability
    for row in rows:
        print("  " + "  |  ".join(str(v) if v is not None else "–" for v in row))


def build_select_query(table_name: str, available_columns: set[str], preferred_columns: list[str], limit: int) -> str:
    selected_columns = [column for column in preferred_columns if column in available_columns]
    if not selected_columns:
        return ""
    order_column = "id" if "id" in available_columns else selected_columns[0]
    return f"""
            SELECT {", ".join(selected_columns)}
            FROM {table_name}
            ORDER BY {order_column} DESC
            LIMIT {limit}
            """


def main() -> int:
    database_path = Path(DATABASE_PATH)

    # Exit early if the database hasn't been created yet
    if not database_path.exists():
        print(f"Database not found: {database_path}")
        return 1

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        sensor_columns = table_columns(cursor, "sensor_data")
        activity_columns = table_columns(cursor, "activity_log")

        # Show the 10 most recent sensor readings including all extended fields
        sensor_query = build_select_query("sensor_data", sensor_columns, SENSOR_COLUMNS, 10)
        if sensor_query:
            print_rows(cursor, sensor_query, "Latest Sensor Readings (10 most recent)")
        else:
            print("\n" + "─" * 60)
            print("  Latest Sensor Readings (10 most recent)")
            print("─" * 60)
            print("  (table sensor_data not available)")

        # Show the 20 most recent activity log entries including severity
        activity_query = build_select_query("activity_log", activity_columns, ACTIVITY_COLUMNS, 20)
        if activity_query:
            print_rows(cursor, activity_query, "Latest Activity Log (20 most recent)")
        else:
            print("\n" + "─" * 60)
            print("  Latest Activity Log (20 most recent)")
            print("─" * 60)
            print("  (table activity_log not available)")

        # Summary: how many alerts were published at each severity level
        if {"event_type", "severity"}.issubset(activity_columns):
            print_rows(
                cursor,
                """
                SELECT severity, COUNT(*) as count
                FROM activity_log
                WHERE event_type = 'alert_published'
                GROUP BY severity
                ORDER BY count DESC
                """,
                "Alert Summary by Severity",
            )
        else:
            print("\n" + "─" * 60)
            print("  Alert Summary by Severity")
            print("─" * 60)
            print("  (severity columns not available in this database schema)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
