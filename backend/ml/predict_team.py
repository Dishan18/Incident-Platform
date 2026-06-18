from backend.ml.model_registry import get_model

def predict_team(description: str):
    model = get_model("team")
    return model.predict([description])[0]