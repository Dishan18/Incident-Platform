"""
SQLAlchemy-based database repository for Incident records.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.database.db import SessionLocal
from backend.database.models import Incident


def create_incident(incident: Incident) -> Incident:
    """Insert a new incident record into the database."""
    session = SessionLocal()
    try:
        session.add(incident)
        session.commit()
        session.refresh(incident)
        return incident
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_incident(incident_id: str) -> Optional[Incident]:
    """Retrieve a single incident by its ID."""
    session = SessionLocal()
    try:
        # Returns the object detached from session to avoid thread issues
        incident = session.query(Incident).filter(Incident.incident_id == incident_id).first()
        if incident:
            session.expunge(incident)
        return incident
    finally:
        session.close()


def get_all_incidents() -> List[Incident]:
    """Retrieve all incidents sorted by creation date (newest first)."""
    session = SessionLocal()
    try:
        incidents = session.query(Incident).order_by(Incident.created_at.desc()).all()
        # Expunge all objects from session
        for inc in incidents:
            session.expunge(inc)
        return incidents
    finally:
        session.close()


def update_status(
    incident_id: str,
    new_status: str,
    timestamp_field: Optional[str] = None,
    timestamp_val: Optional[datetime] = None,
    actual_resolution_time: Optional[int] = None,
    sla_breached: Optional[bool] = None,
) -> bool:
    """Update status, operational timestamps, and resolution metrics."""
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            return False

        incident.status = new_status
        if timestamp_field and hasattr(incident, timestamp_field):
            setattr(incident, timestamp_field, timestamp_val)

        if new_status == "Resolved" and actual_resolution_time is not None:
            incident.actual_resolution_time = actual_resolution_time

        if sla_breached is not None:
            incident.sla_breached = sla_breached

        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def update_overrides(
    incident_id: str,
    team: str,
    priority: str,
    root_cause: str,
    team_overridden: bool,
    priority_overridden: bool,
    resolution_time: Optional[int] = None,
) -> bool:
    """Update operational team assignment, priority, root cause, and actual resolution duration."""
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            return False

        incident.assigned_team = team
        incident.priority = priority
        incident.root_cause = root_cause
        incident.team_overridden = team_overridden
        incident.priority_overridden = priority_overridden
        incident.actual_resolution_time = resolution_time

        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def update_sla_pause_log(incident_id: str, pause_log_json: str) -> bool:
    """Persist the updated SLA pause-log JSON string for an incident."""
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            return False
        incident.sla_pause_log = pause_log_json
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def update_l3_escalation(
    incident_id: str,
    risk: int,
    recommended: bool,
    team: str,
    reasons: list,
) -> bool:
    """Persist L3 escalation analysis results to the database."""
    import json
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            return False
        incident.l3_escalation_risk = risk
        incident.l3_escalation_recommended = recommended
        incident.l3_escalation_team = team
        incident.l3_escalation_reasons = json.dumps(reasons)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def update_rca(
    incident_id: str,
    rca_content: str,
    rca_generated_at: datetime,
    rca_pdf_url: Optional[str] = None,
) -> bool:
    """Persist the generated RCA content and metadata to the database."""
    session = SessionLocal()
    try:
        incident = session.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            return False
        incident.rca_generated = True
        incident.rca_content = rca_content
        incident.rca_generated_at = rca_generated_at
        if rca_pdf_url is not None:
            incident.rca_pdf_url = rca_pdf_url
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()