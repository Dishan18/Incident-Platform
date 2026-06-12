from backend.ml.predict_priority import predict_priority
from backend.ml.predict_resolution import predict_resolution
from backend.ml.predict_team import predict_team


def predict_incident(
    description: str,
    application: str,
    affected_users: int,
    impact_scope: str
):
    """
    Complete incident prediction pipeline.
    """

    team = predict_team(
        description
    )

    priority = predict_priority(
        description=description,
        application=application,
        affected_users=affected_users,
        impact_scope=impact_scope
    )

    resolution_time = predict_resolution(
        description=description,
        application=application,
        priority=priority,
        primary_team=team,
        affected_users=affected_users,
        impact_scope=impact_scope
    )

    return {
        "team": team,
        "priority": priority,
        "resolution_time": round(
            resolution_time,
            2
        )
    }
