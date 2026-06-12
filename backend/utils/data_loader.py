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
    """Load live incidents from CSV.

    If the file does not exist an empty DataFrame with the correct
    schema is created and persisted automatically.
    """
    if not LIVE_FILE.exists():
        df = pd.DataFrame(columns=LIVE_COLUMNS)
        df.to_csv(LIVE_FILE, index=False)
        return df

    df = pd.read_csv(LIVE_FILE)
    for col in _DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def save_live_incidents(df: pd.DataFrame) -> None:
    """Persist the live incidents DataFrame back to CSV."""
    df.to_csv(LIVE_FILE, index=False)


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
