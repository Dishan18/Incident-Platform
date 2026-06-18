from datetime import datetime
import json
from backend.database.db import SessionLocal
from backend.database.models import Incident
from backend.database.incident_repository import create_incident, get_incident
from backend.incident.generate_rca import generate_rca, build_rca_pdf, get_rca_pdf_filename

# Test case input
incident_id = "INC-TEST-RCA-999"

# Ensure clean state
session = SessionLocal()
existing = session.query(Incident).filter(Incident.incident_id == incident_id).first()
if existing:
    session.delete(existing)
    session.commit()
session.close()

# Create test incident
inc = Incident(
    incident_id=incident_id,
    description="VPN outage affecting 5000 users in branch office.",
    application="VPN Gateway",
    affected_users=5000,
    impact_scope="enterprise",
    environment="Production",
    category="Network",
    priority="P1",
    status="Resolved",
    created_at=datetime.now(),
    resolved_at=datetime.now(),
    actual_resolution_time=45,
    sla_breached=False
)
create_incident(inc)
print(f"Created test incident {incident_id}")

try:
    # Run RCA generation
    print("Running generate_rca...")
    rca_report = generate_rca(
        incident_id=incident_id,
        actual_root_cause="Expired VPN certificate.",
        resolution_action="Certificate renewed and tunnel re-established.",
        preventive_measure="Enable certificate expiry monitoring.",
        additional_notes="None"
    )
    print("RCA generated successfully:")
    print(json.dumps(rca_report, indent=2))

    # Reload incident
    db_inc = get_incident(incident_id)
    print("Incident rca_generated status in DB:", db_inc.rca_generated)
    print("Incident rca_content in DB:", db_inc.rca_content)
    print("Incident rca_generated_at in DB:", db_inc.rca_generated_at)
    print("Incident rca_pdf_url in DB:", db_inc.rca_pdf_url)

    # Run PDF building
    print("Building PDF...")
    # Convert incident object to dictionary like frontend does
    from backend.incident.incident_repository import get_incident_by_id
    inc_dict = get_incident_by_id(incident_id)
    pdf_bytes = build_rca_pdf(inc_dict)
    print(f"PDF built successfully: {len(pdf_bytes)} bytes")

    filename = get_rca_pdf_filename(inc_dict)
    print(f"PDF Filename generated: {filename}")

    # Write PDF file to workspace to inspect
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF saved to {filename}")

finally:
    # Cleanup
    session = SessionLocal()
    existing = session.query(Incident).filter(Incident.incident_id == incident_id).first()
    if existing:
        session.delete(existing)
        session.commit()
    session.close()
    print("Cleaned up test incident.")

    import os
    if 'filename' in locals() and os.path.exists(filename):
        os.remove(filename)
        print(f"Cleaned up generated file: {filename}")
