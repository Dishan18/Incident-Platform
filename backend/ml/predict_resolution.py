from pathlib import Path
import pandas as pd
import joblib

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "resolution_model.pkl"
)

model = joblib.load(
    MODEL_PATH
)

def predict_resolution(
    description,
    application,
    priority,
    primary_team,
    affected_users,
    impact_scope
):

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