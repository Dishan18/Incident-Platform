from pathlib import Path
import pandas as pd
import joblib

from backend.ml.model_registry import get_model

def predict_priority(
    description,
    application,
    affected_users,
    impact_scope
):
    model = get_model("priority")

    sample = pd.DataFrame(
        [{
            "description": description,
            "application": application,
            "affected_users": affected_users,
            "impact_scope": impact_scope
        }]
    )

    prediction = model.predict(
        sample
    )[0]

    return prediction