import os
import sys

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.ml.l3_escalation_advisor import analyze_l3_escalation, run_fallback_rules

print("--- TESTING L3 ESCALATION ADVISOR ---\n")

# Test case 1: Oracle DB outage affecting 5000 users
incident_1 = {
    "description": "Oracle DB outage affecting production transactions and databases.",
    "application": "Oracle DB",
    "affected_users": 5000,
    "impact_scope": "enterprise",
    "priority": "P1",
    "predicted_priority": "P1",
    "predicted_team": "Database",
    "predicted_resolution_time": 300,
    "sla_risk": {
        "sla_breached": False,
        "sla_remaining_minutes": 10
    }
}
similar_1 = [
    {
        "description": "Oracle database instance crash due to memory limit",
        "team": "Database",
        "priority": "P1",
        "resolution_time": 280,
        "root_cause": "Oracle SGA memory size exceeded parameters"
    }
]
rc_analysis_1 = {
    "root_cause": "Oracle SGA Memory Exhaustion",
    "confidence": 90,
    "explanation": "Memory limits were exceeded causing transactional failure.",
    "investigation_steps": ["Verify database SGA sizing", "Check DB error log"]
}

print("Running Case 1: Oracle DB Outage (should recommend escalation and risk > 80)")
res_1 = analyze_l3_escalation(incident_1, similar_1, rc_analysis_1)
print(f"Risk Score: {res_1['risk_score']}")
print(f"Escalate: {res_1['escalate']}")
print(f"Recommended Team: {res_1['recommended_team']}")
print(f"Reasons: {res_1['reasons']}\n")

# Test case 2: VPN outage affecting enterprise users
incident_2 = {
    "description": "VPN connection down for all offshore departments.",
    "application": "VPN Gateway",
    "affected_users": 1500,
    "impact_scope": "enterprise",
    "priority": "P2",
    "predicted_priority": "P2",
    "predicted_team": "Network",
    "predicted_resolution_time": 250,
    "sla_risk": {
        "sla_breached": False,
        "sla_remaining_minutes": 45
    }
}
similar_2 = [
    {
        "description": "VPN gateway link failure caused by routing table corruption",
        "team": "Network",
        "priority": "P1",
        "resolution_time": 180,
        "root_cause": "Routing table corruption"
    }
]
rc_analysis_2 = {
    "root_cause": "IPSec Tunnel Loss",
    "confidence": 85,
    "explanation": "Tunnel lost connectivity due to route issues.",
    "investigation_steps": ["Check IPSec Phase 2 status"]
}

print("Running Case 2: VPN Outage (should recommend escalation and risk > 75)")
res_2 = analyze_l3_escalation(incident_2, similar_2, rc_analysis_2)
print(f"Risk Score: {res_2['risk_score']}")
print(f"Escalate: {res_2['escalate']}")
print(f"Recommended Team: {res_2['recommended_team']}")
print(f"Reasons: {res_2['reasons']}\n")

# Test case 3: Single-user IIS issue
incident_3 = {
    "description": "IIS site not loading for single developer in testing sandbox.",
    "application": "IIS Server",
    "affected_users": 1,
    "impact_scope": "user",
    "priority": "P4",
    "predicted_priority": "P4",
    "predicted_team": "Wintel",
    "predicted_resolution_time": 30,
    "sla_risk": {
        "sla_breached": False,
        "sla_remaining_minutes": 2800
    }
}
similar_3 = []
rc_analysis_3 = "Check IIS worker process configuration."

print("Running Case 3: Single-user IIS issue (should NOT recommend escalation and risk < 30)")
res_3 = analyze_l3_escalation(incident_3, similar_3, rc_analysis_3)
print(f"Risk Score: {res_3['risk_score']}")
print(f"Escalate: {res_3['escalate']}")
print(f"Recommended Team: {res_3['recommended_team']}")
print(f"Reasons: {res_3['reasons']}\n")

# Test case 4: Gemini unavailable (simulated fallback)
print("Running Case 4: Gemini Unavailable (fallback rules execute successfully)")
res_fallback = run_fallback_rules(
    priority="P1",
    affected_users=5000,
    impact_scope="enterprise",
    predicted_resolution_time=300,
    predicted_team="Database"
)
print(f"Fallback Risk Score: {res_fallback['risk_score']} (Expected 100)")
print(f"Fallback Escalate: {res_fallback['escalate']} (Expected True)")
print(f"Fallback Reasons: {res_fallback['reasons']}")
