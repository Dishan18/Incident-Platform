"""
Incident status update logic with strict ITSM workflow enforcement.

Allowed transitions
-------------------
Open       -> Assigned | Cancelled
Assigned   -> In Progress | Cancelled
In Progress -> Resolved
Resolved   -> Closed
Closed     -> (terminal)
Cancelled  -> (terminal)
"""

from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd

from backend.utils.data_loader import load_live_incidents, save_live_incidents


VALID_TRANSITIONS: Dict[str, List[str]] = {
    "Open": ["Assigned", "Cancelled"],
    "Assigned": ["In Progress", "Cancelled"],
    "In Progress": ["Resolved"],
    "Resolved": ["Closed"],
    "Closed": [],
    "Cancelled": [],
}

STATUS_TIMESTAMP_MAP: Dict[str, str] = {
    "Assigned": "assigned_at",
    "In Progress": "in_progress_at",
    "Resolved": "resolved_at",
    "Closed": "closed_at",
}

ALL_STATUSES: List[str] = [
    "Open",
    "Assigned",
    "In Progress",
    "Resolved",
    "Closed",
    "Cancelled",
]


def get_valid_transitions(current_status: str) -> List[str]:
    """Return the list of valid next statuses from *current_status*."""
    return VALID_TRANSITIONS.get(current_status, [])


def update_incident_status(
    incident_id: str,
    new_status: str,
) -> Tuple[bool, str]:
    """Update an incident's status following ITSM workflow rules.

    Parameters
    ----------
    incident_id : str
        The unique incident identifier.
    new_status : str
        The desired new status.

    Returns
    -------
    tuple[bool, str]
        ``(success, message)``
    """
    live_df = load_live_incidents()

    mask = live_df["incident_id"] == incident_id
    if not mask.any():
        return False, f"Incident {incident_id} not found."

    idx = live_df[mask].index[0]
    current_status: str = str(live_df.at[idx, "status"])

    valid_next = get_valid_transitions(current_status)
    if new_status not in valid_next:
        valid_str = ", ".join(valid_next) if valid_next else "None (terminal state)"
        return False, (
            f"Invalid transition: {current_status} -> {new_status}. "
            f"Valid: {valid_str}"
        )

    # ── Apply update ──
    live_df.at[idx, "status"] = new_status

    # Set corresponding timestamp
    timestamp_field = STATUS_TIMESTAMP_MAP.get(new_status)
    if timestamp_field:
        live_df.at[idx, timestamp_field] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # Calculate resolution_time when resolved
    if new_status == "Resolved":
        created = pd.to_datetime(live_df.at[idx, "created_at"])
        resolved = datetime.now()
        resolution_minutes = int((resolved - created).total_seconds() / 60)
        live_df.at[idx, "resolution_time"] = resolution_minutes

    save_live_incidents(live_df)
    return True, f"Status updated to {new_status}."
