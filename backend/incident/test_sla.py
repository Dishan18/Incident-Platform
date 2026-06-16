from datetime import datetime, timedelta
from backend.database.db import SessionLocal
from backend.database.models import Incident
from backend.incident.update_incident import update_incident_status

def test_sla_transitions():
    session = SessionLocal()
    test_id = "INC-TEST-SLA01"
    
    # Clean up test incident if exists
    session.query(Incident).filter(Incident.incident_id == test_id).delete()
    session.commit()
    
    try:
        # 1. Create a P1 incident that was logged 2 hours ago (SLA is 1 hour, so it should be breached)
        created_time = datetime.now() - timedelta(hours=2)
        incident = Incident(
            incident_id=test_id,
            description="High priority network fail",
            application="Firewall",
            affected_users=1000,
            impact_scope="site",
            environment="Production",
            category="Security",
            ai_predicted_team="Network",
            ai_predicted_priority="P1",
            ai_predicted_resolution_time=45.0,
            assigned_team="Network",
            priority="P1",
            status="In Progress",
            created_at=created_time,
            sla_breached=False # Starts as false in database
        )
        session.add(incident)
        session.commit()
        
        print("Created incident in session.")
        
        # Transition to Resolved. Since it was logged 2 hours ago and P1 SLA is 1 hour, it should be marked as breached!
        success, message = update_incident_status(test_id, "Resolved")
        print(f"Update response: success={success}, msg={message}")
        
        # Verify database record
        session.expire_all()
        updated_inc = session.query(Incident).filter(Incident.incident_id == test_id).first()
        print(f"Incident priority={updated_inc.priority}, status={updated_inc.status}, sla_breached={updated_inc.sla_breached}")
        
        assert updated_inc.sla_breached == True, "P1 ticket resolved after 2 hours should have breached SLA!"
        print("SLA breach test (late resolution) passed successfully!")
        
        # 2. Test an incident completed within SLA
        test_id_met = "INC-TEST-SLA02"
        session.query(Incident).filter(Incident.incident_id == test_id_met).delete()
        session.commit()
        
        created_time_met = datetime.now() - timedelta(minutes=20) # Logged 20 mins ago, P1 SLA is 60 mins
        incident_met = Incident(
            incident_id=test_id_met,
            description="Quick resolved ticket",
            application="Firewall",
            affected_users=10,
            impact_scope="single_user",
            environment="Production",
            category="Security",
            ai_predicted_team="Network",
            ai_predicted_priority="P1",
            ai_predicted_resolution_time=15.0,
            assigned_team="Network",
            priority="P1",
            status="In Progress",
            created_at=created_time_met,
            sla_breached=False
        )
        session.add(incident_met)
        session.commit()
        
        # Transition to Resolved
        success, message = update_incident_status(test_id_met, "Resolved")
        print(f"Update response: success={success}, msg={message}")
        
        session.expire_all()
        updated_inc_met = session.query(Incident).filter(Incident.incident_id == test_id_met).first()
        print(f"Incident status={updated_inc_met.status}, sla_breached={updated_inc_met.sla_breached}")
        
        assert updated_inc_met.sla_breached == False, "P1 ticket resolved after 20 minutes should NOT have breached SLA!"
        print("SLA met test (early resolution) passed successfully!")
        
    finally:
        # Clean up
        session.query(Incident).filter(Incident.incident_id == test_id).delete()
        session.query(Incident).filter(Incident.incident_id == test_id_met).delete()
        session.commit()
        session.close()

if __name__ == "__main__":
    test_sla_transitions()
