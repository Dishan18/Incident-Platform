from backend.ml.predict_team import predict_team

print(
    predict_team(
        "VPN connection failed in production"
    )
)

print(
    predict_team(
        "Oracle listener unavailable"
    )
)

print(
    predict_team(
        "Kafka consumer lag detected"
    )
)
