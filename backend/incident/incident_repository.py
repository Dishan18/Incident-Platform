"""
Incident data access layer.
Provides query helpers for live incident data used by the frontend.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd

from backend.utils.data_loader import load_live_incidents


def get_live_incidents() -> pd.DataFrame:
    """Return all live incidents sorted by creation date (newest first)."""
    df = load_live_incidents()
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df = df.sort_values("created_at", ascending=False).reset_index(drop=True)
    return df


def get_incident_by_id(incident_id: str) -> Optional[dict]:
    """Fetch a single incident by its ID. Returns ``None`` if not found."""
    df = load_live_incidents()
    match = df[df["incident_id"] == incident_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_incidents_grouped_by_date() -> Dict[str, List[dict]]:
    """Group live incidents by date for timeline display.

    Returns a dict mapping human-readable date labels
    (``"Today"``, ``"Yesterday"``, or ``"June 10, 2026"``)
    to lists of incident dicts.
    """
    df = get_live_incidents()
    if df.empty:
        return {}

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    groups: Dict[str, List[dict]] = {}
    for _, row in df.iterrows():
        created = row["created_at"]
        if pd.isna(created):
            continue

        if hasattr(created, "date"):
            incident_date = created.date()
        else:
            incident_date = pd.to_datetime(created).date()

        if incident_date == today:
            label = "Today"
        elif incident_date == yesterday:
            label = "Yesterday"
        else:
            label = incident_date.strftime("%B %d, %Y")

        if label not in groups:
            groups[label] = []
        groups[label].append(row.to_dict())

    return groups
