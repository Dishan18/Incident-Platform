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

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd

from backend.database.incident_repository import get_incident as db_get_incident
from backend.database.incident_repository import update_status as db_update_status
from backend.database.incident_repository import update_sla_pause_log as db_update_sla_pause_log

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

SLA_HOURS: Dict[str, int] = {"P1": 1, "P2": 3, "P3": 8, "P4": 48}

_TS_FMT = "%Y-%m-%d %H:%M:%S"


# ── Pause-log helpers ────────────────────────────────────────────────────

def _parse_pause_log(raw: str | None) -> list:
    """Safely deserialize the JSON pause-log string."""
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


def compute_total_paused_seconds(pause_log: list, up_to: datetime | None = None) -> float:
    """Return the total number of seconds the SLA clock was paused.

    ``up_to`` defaults to *now* and is used to cap an open (un-resumed) hold.
    """
    if up_to is None:
        up_to = datetime.now()

    total = 0.0
    hold_start = None

    for entry in pause_log:
        ts = datetime.strptime(entry["at"], _TS_FMT)
        if entry["action"] == "hold":
            hold_start = ts
        elif entry["action"] == "resume" and hold_start is not None:
            total += (ts - hold_start).total_seconds()
            hold_start = None

    # If currently on hold (no matching resume), count up to *up_to*
    if hold_start is not None:
        total += (up_to - hold_start).total_seconds()

    return total


def is_currently_on_hold(pause_log: list) -> bool:
    """Return True when the last entry is a 'hold' (no matching resume)."""
    if not pause_log:
        return False
    return pause_log[-1].get("action") == "hold"


# ── Public API ───────────────────────────────────────────────────────────

def get_valid_transitions(current_status: str) -> List[str]:
    """Return the list of valid next statuses from *current_status*."""
    return VALID_TRANSITIONS.get(current_status, [])


def hold_incident_sla(incident_id: str) -> Tuple[bool, str]:
    """Pause the SLA clock for an In-Progress incident."""
    incident = db_get_incident(incident_id)
    if not incident:
        return False, f"Incident {incident_id} not found."
    if incident.status != "In Progress":
        return False, "SLA can only be held for incidents that are In Progress."

    pause_log = _parse_pause_log(incident.sla_pause_log)
    if is_currently_on_hold(pause_log):
        return False, "SLA is already on hold."

    pause_log.append({"action": "hold", "at": datetime.now().strftime(_TS_FMT)})
    ok = db_update_sla_pause_log(incident_id, json.dumps(pause_log))
    if ok:
        return True, "SLA clock paused."
    return False, "Failed to update pause log."


def resume_incident_sla(incident_id: str) -> Tuple[bool, str]:
    """Resume the SLA clock for an incident currently on hold."""
    incident = db_get_incident(incident_id)
    if not incident:
        return False, f"Incident {incident_id} not found."

    pause_log = _parse_pause_log(incident.sla_pause_log)
    if not is_currently_on_hold(pause_log):
        return False, "SLA is not currently on hold."

    pause_log.append({"action": "resume", "at": datetime.now().strftime(_TS_FMT)})
    ok = db_update_sla_pause_log(incident_id, json.dumps(pause_log))
    if ok:
        return True, "SLA clock resumed."
    return False, "Failed to update pause log."


def update_incident_status(
    incident_id: str,
    new_status: str,
) -> Tuple[bool, str]:
    """Update an incident's status following ITSM workflow rules in the database."""
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

    # If currently on hold and transitioning away from In Progress, auto-resume first
    pause_log = _parse_pause_log(incident.sla_pause_log)
    if is_currently_on_hold(pause_log) and current_status == "In Progress":
        pause_log.append({"action": "resume", "at": datetime.now().strftime(_TS_FMT)})
        db_update_sla_pause_log(incident_id, json.dumps(pause_log))

    # Determine timestamps
    timestamp_field = STATUS_TIMESTAMP_MAP.get(new_status)
    timestamp_val = datetime.now() if timestamp_field else None

    # Calculate actual resolution time when resolved
    actual_res_time = None
    if new_status == "Resolved" and incident.created_at:
        created = incident.created_at
        resolved = datetime.now()
        actual_res_time = int((resolved - created).total_seconds() / 60)

    # Calculate SLA breach state (accounting for paused time)
    sla_breached = None
    if new_status in ("Resolved", "Closed") and incident.created_at and incident.priority in SLA_HOURS:
        paused_secs = compute_total_paused_seconds(pause_log)
        deadline = incident.created_at + timedelta(hours=SLA_HOURS[incident.priority]) + timedelta(seconds=paused_secs)

        completion_time = None
        if new_status == "Resolved":
            completion_time = timestamp_val or datetime.now()
        elif new_status == "Closed":
            completion_time = incident.resolved_at or timestamp_val or datetime.now()

        if completion_time:
            if isinstance(completion_time, str):
                completion_time = datetime.strptime(completion_time, _TS_FMT)
            sla_breached = completion_time > deadline

    # Perform update
    success = db_update_status(
        incident_id=incident_id,
        new_status=new_status,
        timestamp_field=timestamp_field,
        timestamp_val=timestamp_val,
        actual_resolution_time=actual_res_time,
        sla_breached=sla_breached,
    )

    if success:
        return True, f"Status updated to {new_status}."
    return False, "Failed to update status in database."
