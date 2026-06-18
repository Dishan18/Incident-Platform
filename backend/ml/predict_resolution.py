from pathlib import Path
import pandas as pd
import joblib

from backend.ml.model_registry import get_model

def predict_resolution(
    description,
    application,
    priority,
    primary_team,
    affected_users,
    impact_scope
) -> float:
    try:
        model = get_model("resolution")

        sample = pd.DataFrame(
            [{
                "description": description,
                "application": application,
                "priority": priority,
                "primary_team": primary_team,
                "affected_users": affected_users,
                "impact_scope": impact_scope
            }]
        )

        prediction = model.predict(
            sample
        )[0]

        return round(float(prediction), 2)
    except Exception as e:
        print(f"predict_resolution model load failed, running fallback heuristics: {e}")
        prio = str(priority).upper()
        if prio == "P1":
            return 30.0
        elif prio == "P2":
            return 60.0
        elif prio == "P3":
            return 180.0
        elif prio == "P4":
            return 360.0
        return 120.0