"""Migration: add RCA Generator columns to live_incidents table."""

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

        altered = False
        if "rca_generated" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN rca_generated BOOLEAN DEFAULT 0")
            print("Added column 'rca_generated'")
            altered = True

        if "rca_content" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN rca_content TEXT")
            print("Added column 'rca_content'")
            altered = True

        if "rca_generated_at" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN rca_generated_at DATETIME")
            print("Added column 'rca_generated_at'")
            altered = True

        if altered:
            conn.commit()
            print("Successfully migrated database tables for RCA Generator.")
        else:
            print("All RCA Generator columns already exist.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
