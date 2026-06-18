"""Migration: add rca_pdf_url column to live_incidents table."""

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

        if "rca_pdf_url" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN rca_pdf_url TEXT")
            conn.commit()
            print("Added column 'rca_pdf_url' to live_incidents.")
        else:
            print("Column 'rca_pdf_url' already exists.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
