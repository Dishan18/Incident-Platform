"""
Data loading and persistence utilities.
Handles all CSV I/O for both historical and live incident data.
"""

from pathlib import Path
from typing import List

import pandas as pd


BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = BASE_DIR / "data"
HISTORICAL_FILE: Path = DATA_DIR / "synthetic_tickets.csv"
LIVE_FILE: Path = DATA_DIR / "live_incidents.csv"

LIVE_COLUMNS: List[str] = [
    "incident_id",
    "description",
    "application",
    "affected_users",
    "impact_scope",
    "environment",
    "category",
    "teams",
    "priority",
    "status",
    "root_cause",
    "resolution_time",
    "created_at",
    "assigned_at",
    "in_progress_at",
    "resolved_at",
    "closed_at",
]

_DATE_COLUMNS: List[str] = [
    "created_at",
    "assigned_at",
    "in_progress_at",
    "resolved_at",
    "closed_at",
]


def load_historical_data() -> pd.DataFrame:
    """Load the historical synthetic tickets dataset.

    Renames ``ticket_id`` to ``incident_id`` so both datasets share
    a common identifier column.
    """
    df = pd.read_csv(HISTORICAL_FILE)
    df = df.rename(columns={"ticket_id": "incident_id"})
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    return df


def load_live_incidents() -> pd.DataFrame:
    """Load live incidents from the SQLite database."""
    from backend.database.db import SessionLocal
    from backend.database.models import Incident

    session = SessionLocal()
    try:
        incidents = session.query(Incident).all()
        rows = []
        for inc in incidents:
            rows.append({
                "incident_id": inc.incident_id,
                "description": inc.description,
                "application": inc.application,
                "affected_users": inc.affected_users,
                "impact_scope": inc.impact_scope,
                "environment": inc.environment,
                "category": inc.category,
                
                # AI predictions
                "predicted_team": inc.ai_predicted_team,
                "predicted_priority": inc.ai_predicted_priority,
                "predicted_resolution_time": inc.ai_predicted_resolution_time,
                
                # active operational fields
                "teams": inc.assigned_team if (inc.assigned_team is not None and str(inc.assigned_team).strip() != "") else inc.ai_predicted_team,
                "priority": inc.priority,
                "status": inc.status,
                "root_cause": inc.root_cause,
                "resolution_time": inc.actual_resolution_time if inc.actual_resolution_time is not None else "",
                
                "team_overridden": inc.team_overridden,
                "priority_overridden": inc.priority_overridden,
                
                # timestamps
                "created_at": inc.created_at,
                "assigned_at": inc.assigned_at,
                "in_progress_at": inc.in_progress_at,
                "resolved_at": inc.resolved_at,
                "closed_at": inc.closed_at
            })
        df = pd.DataFrame(rows, columns=LIVE_COLUMNS)
        for col in _DATE_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df
    finally:
        session.close()


def save_live_incidents(df: pd.DataFrame) -> None:
    """Save live incidents back to SQLite (Legacy CSV wrapper)."""
    pass


def get_all_incidents() -> pd.DataFrame:
    """Merge historical and live data for unified KPI calculations.

    Columns present in one dataset but not the other are filled
    with ``None`` so the concat succeeds cleanly.
    """
    historical = load_historical_data()
    live = load_live_incidents()

    if live.empty:
        return historical

    for col in historical.columns:
        if col not in live.columns:
            live[col] = None
    for col in live.columns:
        if col not in historical.columns:
            historical[col] = None

    return pd.concat([historical, live], ignore_index=True)
