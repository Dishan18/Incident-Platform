"""Migration: add sla_pause_log TEXT column to live_incidents table."""

import sqlite3
import os


def migrate():
    db_path = "incident.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Schema will be created clean when init_db runs.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(live_incidents)")
        columns = [row[1] for row in cursor.fetchall()]

        if "sla_pause_log" not in columns:
            cursor.execute(
                "ALTER TABLE live_incidents ADD COLUMN sla_pause_log TEXT DEFAULT '[]'"
            )
            conn.commit()
            print("Successfully added 'sla_pause_log' column to 'live_incidents' table.")
        else:
            print("Column 'sla_pause_log' already exists in 'live_incidents' table.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
