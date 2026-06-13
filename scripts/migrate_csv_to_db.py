"""
Migration script: CSV to SQLite.
Reads live_incidents.csv and populates the SQLite live_incidents table.
"""

import os
import sys
from datetime import datetime
import pandas as pd

# Set up path to include root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.db import SessionLocal
from backend.database.models import Incident


def parse_date(val):
    if pd.isna(val) or not str(val).strip():
        return None
    try:
        # Try custom format
        return datetime.strptime(str(val).strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Fallback
            return pd.to_datetime(val).to_pydatetime()
        except Exception:
            return None


def migrate():
    csv_path = "data/live_incidents.csv"
    if not os.path.exists(csv_path):
        print("CSV file not found, skipping migration.")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print("CSV is empty, nothing to migrate.")
        return

    session = SessionLocal()
    try:
        # Clear existing records in SQL to prevent duplicates
        session.query(Incident).delete()
        session.commit()

        count = 0
        for _, row in df.iterrows():
            iid = str(row.get("incident_id"))
            desc = str(row.get("description", ""))
            app = str(row.get("application", ""))
            users = int(row.get("affected_users", 1)) if not pd.isna(row.get("affected_users")) else 1
            scope = str(row.get("impact_scope", ""))
            env = str(row.get("environment", ""))
            cat = str(row.get("category", ""))

            # Predicted mapping
            ai_team = str(row.get("predicted_team", ""))
            ai_priority = str(row.get("predicted_priority", ""))
            ai_res_time = float(row.get("predicted_resolution_time", 0.0)) if not pd.isna(row.get("predicted_resolution_time")) else 0.0

            # Operational values mapping
            assigned_team = str(row.get("teams", ai_team))
            priority = str(row.get("priority", ai_priority))
            root_cause = str(row.get("root_cause", "")) if not pd.isna(row.get("root_cause")) else ""
            status = str(row.get("status", "Open"))

            # Determine override flags
            team_overridden = ai_team != assigned_team
            priority_overridden = ai_priority != priority

            # Resolution Time
            res_val = row.get("resolution_time")
            if pd.isna(res_val) or str(res_val).strip() in ("", "nan", "NaT", "None"):
                actual_res_time = None
            else:
                try:
                    actual_res_time = int(float(res_val))
                except ValueError:
                    actual_res_time = None

            # Datetime parses
            created_at = parse_date(row.get("created_at")) or datetime.now()
            assigned_at = parse_date(row.get("assigned_at"))
            in_progress_at = parse_date(row.get("in_progress_at"))
            resolved_at = parse_date(row.get("resolved_at"))
            closed_at = parse_date(row.get("closed_at"))

            incident = Incident(
                incident_id=iid,
                description=desc,
                application=app,
                affected_users=users,
                impact_scope=scope,
                environment=env,
                category=cat,
                ai_predicted_team=ai_team,
                ai_predicted_priority=ai_priority,
                ai_predicted_resolution_time=ai_res_time,
                assigned_team=assigned_team,
                priority=priority,
                root_cause=root_cause,
                status=status,
                team_overridden=team_overridden,
                priority_overridden=priority_overridden,
                actual_resolution_time=actual_res_time,
                created_at=created_at,
                assigned_at=assigned_at,
                in_progress_at=in_progress_at,
                resolved_at=resolved_at,
                closed_at=closed_at
            )
            session.add(incident)
            count += 1

        session.commit()
        print(f"Successfully migrated {count} incidents from CSV to SQLite database")

    except Exception as e:
        session.rollback()
        print(f"Error during migration: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
