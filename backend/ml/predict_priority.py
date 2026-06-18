from pathlib import Path
import pandas as pd
import joblib

from backend.ml.model_registry import get_model

def predict_priority(
    description,
    application,
    affected_users,
    impact_scope
) -> str:
    try:
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
    except Exception as e:
        print(f"predict_priority model load failed, running fallback heuristics: {e}")
        try:
            users = int(affected_users)
        except (ValueError, TypeError):
            users = 1
        
        scope = str(impact_scope).lower()
        if scope == "enterprise" or users >= 1000:
            return "P1"
        elif scope == "site" or users >= 100:
            return "P2"
        elif scope == "department" or users >= 10:
            return "P3"
        return "P4"