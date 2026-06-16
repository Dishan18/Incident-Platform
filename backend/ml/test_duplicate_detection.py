from backend.ml.similar_incidents import get_similar_incidents
from backend.database.db import SessionLocal
from backend.database.models import Incident
from datetime import datetime

def run_test():
    # Insert a dummy open/active incident
    session = SessionLocal()
    dummy_id = "INC-TEST-DUP01"
    
    # Clean up dummy if it exists
    session.query(Incident).filter(Incident.incident_id == dummy_id).delete()
    session.commit()
    
    try:
        incident = Incident(
            incident_id=dummy_id,
            description="Database lock query latency spike observed",
            application="Oracle DB",
            affected_users=100,
            impact_scope="department",
            environment="Production",
            category="Database",
            ai_predicted_team="Database",
            ai_predicted_priority="P2",
            ai_predicted_resolution_time=120.0,
            assigned_team="Database",
            priority="P2",
            status="In Progress", # Active status
            created_at=datetime.now()
        )
        session.add(incident)
        session.commit()
        
        print("Inserted test active incident.")
        
        # Test similarity search with active_only=True
        matches = get_similar_incidents("Database lock observed in query", top_k=3, active_only=True)
        
        print(f"Active search returned {len(matches)} matches.")
        found = False
        for m in matches:
            print(f"Match: {m['incident_id']} - Similarity: {m['similarity']}% - Description: {m['description']}")
            if m["incident_id"] == dummy_id:
                found = True
                assert m["similarity"] >= 65.0, "Similarity should be high!"
                
        assert found, "The dummy incident should have been found in the active search."
        print("Success! Active similarity search works correctly.")
        
        # Clean up and insert as Closed
        session.query(Incident).filter(Incident.incident_id == dummy_id).delete()
        session.commit()
        
        incident_closed = Incident(
            incident_id=dummy_id,
            description="Database lock query latency spike observed",
            application="Oracle DB",
            affected_users=100,
            impact_scope="department",
            environment="Production",
            category="Database",
            ai_predicted_team="Database",
            ai_predicted_priority="P2",
            ai_predicted_resolution_time=120.0,
            assigned_team="Database",
            priority="P2",
            status="Closed", # Closed status
            created_at=datetime.now()
        )
        session.add(incident_closed)
        session.commit()
        
        print("Inserted test closed incident.")
        matches_closed = get_similar_incidents("Database lock query latency spike observed", top_k=3, active_only=True)
        found_closed = any(m["incident_id"] == dummy_id for m in matches_closed)
        assert not found_closed, "Closed incidents should not be found in active similarity search."
        print("Success! Closed incidents are correctly ignored.")
        
    finally:
        # Clean up
        session.query(Incident).filter(Incident.incident_id == dummy_id).delete()
        session.commit()
        session.close()

if __name__ == "__main__":
    run_test()
