from backend.ml.predict_incident import predict_incident
from datetime import datetime
import pandas as pd

from backend.utils.data_loader import (
    load_live_incidents,
    save_live_incidents,
)

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

    live_df = load_live_incidents()

    # Generate Incident ID
    year = now.year

    if live_df.empty:
        next_num = 1

    else:

        existing_nums = []

        for iid in live_df["incident_id"]:

            try:
                existing_nums.append(
                    int(str(iid).split("-")[-1])
                )

            except (ValueError, IndexError):
                continue

        next_num = max(
            existing_nums,
            default=0,
        ) + 1

    incident_id = f"INC-{year}-{next_num:05d}"

    category = APP_CATEGORY.get(
        application,
        "Unknown",
    )

    # AI prediction pipeline
    prediction = predict_incident(
        description=description,
        application=application,
        affected_users=affected_users,
        impact_scope=impact_scope,
    )

    predicted_team = prediction["team"]
    predicted_priority = prediction["priority"]
    predicted_resolution_time = round(
        prediction["resolution_time"],
        2,
    )

    incident = {
        "incident_id": incident_id,

        "description": description,

        "application": application,

        "affected_users": affected_users,

        "impact_scope": impact_scope,

        "environment": environment,

        "category": category,

        # AI recommendations
        "predicted_team":
            predicted_team,

        "predicted_priority":
            predicted_priority,

        "predicted_resolution_time":
            predicted_resolution_time,

        # workflow fields
        "teams":
            predicted_team,

        "priority":
            predicted_priority,

        "status":
            "Open",

        "root_cause":
            "",

        "resolution_time":
            "",

        "created_at":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "assigned_at":
            "",

        "in_progress_at":
            "",

        "resolved_at":
            "",

        "closed_at":
            "",
    }

    live_df = pd.concat(
        [
            live_df,
            pd.DataFrame([incident]),
        ],
        ignore_index=True,
    )

    save_live_incidents(
        live_df
    )

    return incident
