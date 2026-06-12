from backend.ml.predict_priority import predict_priority

print(
    predict_priority(
        description="VPN connection failed",
        application="VPN Gateway",
        affected_users=5000,
        impact_scope="enterprise"
    )
)

print(
    predict_priority(
        description="User account locked",
        application="Active Directory",
        affected_users=1,
        impact_scope="single_user"
    )
)
