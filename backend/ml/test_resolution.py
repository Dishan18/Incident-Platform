from backend.ml.predict_resolution import predict_resolution

print(
    predict_resolution(
        description="VPN connection failed",
        application="VPN Gateway",
        priority="P1",
        primary_team="Network",
        affected_users=5000,
        impact_scope="enterprise"
    )
)
