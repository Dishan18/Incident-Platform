"""Migration: add L3 Escalation Advisor columns to live_incidents table."""

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
        if "l3_escalation_risk" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN l3_escalation_risk INTEGER")
            print("Added column 'l3_escalation_risk'")
            altered = True

        if "l3_escalation_recommended" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN l3_escalation_recommended BOOLEAN DEFAULT 0")
            print("Added column 'l3_escalation_recommended'")
            altered = True

        if "l3_escalation_reasons" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN l3_escalation_reasons TEXT DEFAULT '[]'")
            print("Added column 'l3_escalation_reasons'")
            altered = True

        if "l3_escalation_team" not in columns:
            cursor.execute("ALTER TABLE live_incidents ADD COLUMN l3_escalation_team TEXT")
            print("Added column 'l3_escalation_team'")
            altered = True

        if altered:
            conn.commit()
            print("Successfully migrated database tables for L3 Escalation Advisor.")
        else:
            print("All L3 Escalation columns already exist.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
