import json
from backend.ml.root_cause_agent import analyze_root_cause

# Mock Current Incident
current = {
    "incident_id": "INC-2026-00009",
    "description": "VPN connection failed for multiple users in the branch office.",
    "application": "VPN Gateway",
    "category": "Connectivity",
    "impact_scope": "enterprise",
    "affected_users": 5000
}

# Mock Similar Historical Incidents
similar = [
    {
        "similarity": 0.89,
        "description": "VPN Tunnel connection dropped between core gateway and branch office.",
        "root_cause": "VPN Tunnel Failure",
        "resolution_time": 45
    },
    {
        "similarity": 0.76,
        "description": "Branch office users reporting connection timeouts when using VPN client.",
        "root_cause": "VPN Gateway overload",
        "resolution_time": 30
    }
]

print("Running Gemini Root Cause Agent Analysis...")
result = analyze_root_cause(current, similar)
print(json.dumps(result, indent=2))
