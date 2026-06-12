from backend.incident.create_incident import create_incident

incident = create_incident(
    description="VPN connection failed for multiple users",
    application="VPN Gateway",
    affected_users=5000,
    impact_scope="enterprise",
    environment="Production",
)

print(incident)