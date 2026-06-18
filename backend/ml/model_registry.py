import os
from pathlib import Path
import joblib
from backend.cloud.azure_blob import download_file

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODELS = {
    "priority": "priority_model.pkl",
    "team": "team_model.pkl",
    "resolution": "resolution_model.pkl"
}

_loaded_models = {}


def ensure_models_exist():
    """Download any missing models from Azure Blob Storage if they do not exist locally."""
    # Ensure directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    for model_key, model_name in MODELS.items():
        model_path = MODEL_DIR / model_name
        if not model_path.exists():
            print(f"Downloading model '{model_name}' from Azure Blob Storage...")
            try:
                download_file(model_name, str(model_path), container_name="models")
                print(f"Successfully downloaded '{model_name}'.")
            except Exception as e:
                print(f"Failed to download model '{model_name}': {e}")


def get_model(model_key: str):
    """Retrieve and lazily load a model by key, ensuring it exists locally."""
    if model_key not in MODELS:
        raise ValueError(f"Unknown model key: {model_key}")

    if model_key not in _loaded_models:
        model_name = MODELS[model_key]
        model_path = MODEL_DIR / model_name

        if not model_path.exists():
            print(f"Model path '{model_path}' not found. Ensuring models exist...")
            ensure_models_exist()

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file '{model_name}' could not be resolved from storage."
            )

        print(f"Loading model '{model_name}' into memory...")
        _loaded_models[model_key] = joblib.load(model_path)

    return _loaded_models[model_key]
