from datetime import datetime
import pandas as pd

from backend.ml.predict_incident import predict_incident
from backend.utils.data_loader import load_live_incidents
from backend.database.models import Incident
from backend.database.incident_repository import create_incident as db_create_incident

APP_TEAM_MAP = {
    "Active Directory": ["Wintel"],
    "DNS Server": ["Wintel"],
    "Windows File Server": ["Wintel"],
    "IIS Server": ["Wintel"],
    "Linux ERP Server": ["Unix/Linux"],
    "Linux Web Server": ["Unix/Linux"],
    "Apache Server": ["Unix/Linux"],
    "NFS Storage": ["Unix/Linux"],
    "VPN Gateway": ["Network"],
    "Firewall": ["Network"],
    "Load Balancer": ["Network"],
    "Oracle DB": ["Database"],
    "SQL Server": ["Database"],
    "PostgreSQL": ["Database"],
    "Tomcat": ["Middleware"],
    "WebSphere": ["Middleware"],
    "Kafka": ["Middleware"],
    "IBM MQ": ["Middleware"],
    "Control-M": ["Batch"],
    "Autosys": ["Batch"],
}

APP_CATEGORY = {
    "Active Directory": "Authentication",
    "DNS Server": "Authentication",
    "Windows File Server": "Windows Infrastructure",
    "IIS Server": "Middleware",
    "Linux ERP Server": "Application",
    "Linux Web Server": "Application",
    "Apache Server": "Middleware",
    "NFS Storage": "Storage",
    "VPN Gateway": "Connectivity",
    "Firewall": "Security",
    "Load Balancer": "Connectivity",
    "Oracle DB": "Database",
    "SQL Server": "Database",
    "PostgreSQL": "Database",
    "Tomcat": "Middleware",
    "WebSphere": "Middleware",
    "Kafka": "Middleware",
    "IBM MQ": "Middleware",
    "Control-M": "Batch Failure",
    "Autosys": "Batch Failure",
}


def create_incident(
    description: str,
    application: str,
    affected_users: int,
    impact_scope: str,
    environment: str,
) -> dict:
    now = datetime.now()

    # Load current live incidents to generate the sequential ID
    live_df = load_live_incidents()
    year = now.year

    if live_df.empty:
        next_num = 1
    else:
        existing_nums = []
        for iid in live_df["incident_id"]:
            try:
                parts = str(iid).split("-")
                if len(parts) == 3 and parts[0] == "INC" and parts[1] == str(year):
                    existing_nums.append(int(parts[2]))
            except (ValueError, IndexError):
                continue
        next_num = max(existing_nums, default=0) + 1

    incident_id = f"INC-{year}-{next_num:05d}"
    category = APP_CATEGORY.get(application, "Unknown")

    # Run prediction pipeline
    prediction = predict_incident(
        description=description,
        application=application,
        affected_users=affected_users,
        impact_scope=impact_scope,
    )

    predicted_team = prediction["team"]
    predicted_priority = prediction["priority"]
    predicted_resolution_time = round(prediction["resolution_time"], 2)

    # Construct SQLAlchemy model object
    incident_obj = Incident(
        incident_id=incident_id,
        description=description,
        application=application,
        affected_users=affected_users,
        impact_scope=impact_scope,
        environment=environment,
        category=category,
        
        # AI Predictions
        ai_predicted_team=predicted_team,
        ai_predicted_priority=predicted_priority,
        ai_predicted_resolution_time=predicted_resolution_time,
        
        # Operational parameters
        assigned_team=predicted_team,
        priority=predicted_priority,
        status="Open",
        root_cause="",
        actual_resolution_time=None,
        team_overridden=False,
        priority_overridden=False,
        
        # Timestamps
        created_at=now,
        assigned_at=None,
        in_progress_at=None,
        resolved_at=None,
        closed_at=None
    )

    # Persist in database
    db_create_incident(incident_obj)

    # Return dict representation for frontend compatibility
    return {
        "incident_id": incident_id,
        "description": description,
        "application": application,
        "affected_users": affected_users,
        "impact_scope": impact_scope,
        "environment": environment,
        "category": category,
        "predicted_team": predicted_team,
        "predicted_priority": predicted_priority,
        "predicted_resolution_time": predicted_resolution_time,
        "teams": predicted_team,
        "priority": predicted_priority,
        "status": "Open",
        "root_cause": "",
        "resolution_time": "",
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "assigned_at": "",
        "in_progress_at": "",
        "resolved_at": "",
        "closed_at": ""
    }
