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
):
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