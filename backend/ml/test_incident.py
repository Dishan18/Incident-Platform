from backend.ml.predict_incident import predict_incident


result = predict_incident(
    description="VPN connection failed for multiple users",
    application="VPN Gateway",
    affected_users=5000,
    impact_scope="enterprise"
)

print(result)
