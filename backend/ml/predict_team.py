from pathlib import Path
import joblib
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "team_model.pkl"
model = joblib.load(MODEL_PATH)
def predict_team(description: str):
    return model.predict([description])[0]