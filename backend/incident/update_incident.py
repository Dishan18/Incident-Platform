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

from backend.database.incident_repository import get_incident as db_get_incident
from backend.database.incident_repository import update_status as db_update_status

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
    """Update an incident's status following ITSM workflow rules in SQLite database."""
    incident = db_get_incident(incident_id)
    if not incident:
        return False, f"Incident {incident_id} not found."

    current_status = incident.status
    valid_next = get_valid_transitions(current_status)

    if new_status not in valid_next:
        valid_str = ", ".join(valid_next) if valid_next else "None (terminal state)"
        return False, (
            f"Invalid transition: {current_status} -> {new_status}. "
            f"Valid: {valid_str}"
        )

    # Determine timestamps
    timestamp_field = STATUS_TIMESTAMP_MAP.get(new_status)
    timestamp_val = datetime.now() if timestamp_field else None

    # Calculate actual resolution time when resolved
    actual_res_time = None
    if new_status == "Resolved" and incident.created_at:
        created = incident.created_at
        resolved = datetime.now()
        actual_res_time = int((resolved - created).total_seconds() / 60)

    # Perform update
    success = db_update_status(
        incident_id=incident_id,
        new_status=new_status,
        timestamp_field=timestamp_field,
        timestamp_val=timestamp_val,
        actual_resolution_time=actual_res_time,
    )

    if success:
        return True, f"Status updated to {new_status}."
    return False, "Failed to update status in database."
