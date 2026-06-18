"""
Incident data access layer.
Provides query helpers for database incident data used by the frontend.
"""

from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta

from backend.utils.data_loader import load_live_incidents
from backend.database.incident_repository import get_incident as db_get_incident


def get_live_incidents() -> pd.DataFrame:
    """Return all live incidents sorted by creation date (newest first)."""
    df = load_live_incidents()
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df = df.sort_values("created_at", ascending=False).reset_index(drop=True)
    return df


def get_incident_by_id(incident_id: str) -> Optional[dict]:
    """Fetch a single incident by its ID. Returns ``None`` if not found."""
    inc = db_get_incident(incident_id)
    if not inc:
        return None

    return {
        "incident_id": inc.incident_id,
        "description": inc.description,
        "application": inc.application,
        "affected_users": inc.affected_users,
        "impact_scope": inc.impact_scope,
        "environment": inc.environment,
        "category": inc.category,
        "predicted_team": inc.ai_predicted_team,
        "predicted_priority": inc.ai_predicted_priority,
        "predicted_resolution_time": inc.ai_predicted_resolution_time,
        "teams": inc.assigned_team if (inc.assigned_team is not None and str(inc.assigned_team).strip() != "") else inc.ai_predicted_team,
        "priority": inc.priority,
        "status": inc.status,
        "root_cause": inc.root_cause,
        "resolution_time": inc.actual_resolution_time if inc.actual_resolution_time is not None else "",
        "created_at": inc.created_at.strftime("%Y-%m-%d %H:%M:%S") if inc.created_at else "",
        "assigned_at": inc.assigned_at.strftime("%Y-%m-%d %H:%M:%S") if inc.assigned_at else "",
        "in_progress_at": inc.in_progress_at.strftime("%Y-%m-%d %H:%M:%S") if inc.in_progress_at else "",
        "resolved_at": inc.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if inc.resolved_at else "",
        "closed_at": inc.closed_at.strftime("%Y-%m-%d %H:%M:%S") if inc.closed_at else "",
        "sla_breached": inc.sla_breached,
        "sla_pause_log": inc.sla_pause_log if inc.sla_pause_log else "[]",
        "rca_generated": inc.rca_generated if hasattr(inc, "rca_generated") else False,
        "rca_content": inc.rca_content if hasattr(inc, "rca_content") else None,
        "rca_generated_at": inc.rca_generated_at.strftime("%Y-%m-%d %H:%M:%S") if (hasattr(inc, "rca_generated_at") and inc.rca_generated_at) else "",
        "rca_pdf_url": inc.rca_pdf_url if hasattr(inc, "rca_pdf_url") else None,
        "l3_escalation_risk": inc.l3_escalation_risk if hasattr(inc, "l3_escalation_risk") else None,
        "l3_escalation_recommended": inc.l3_escalation_recommended if hasattr(inc, "l3_escalation_recommended") else False,
        "l3_escalation_reasons": inc.l3_escalation_reasons if hasattr(inc, "l3_escalation_reasons") else "[]",
        "l3_escalation_team": inc.l3_escalation_team if hasattr(inc, "l3_escalation_team") else None,
    }


def get_incidents_grouped_by_date() -> Dict[str, List[dict]]:
    """Group live incidents by date for timeline display."""
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
