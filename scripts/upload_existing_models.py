"""One-off script to seed existing models from local models directory to Azure Blob Storage container 'models'."""

import os
from pathlib import Path
from backend.cloud.azure_blob import upload_file

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODELS = ["priority_model.pkl", "team_model.pkl", "resolution_model.pkl"]


def main():
    print("Starting upload of local models to Azure Blob Storage...")
    for model_name in MODELS:
        model_path = MODEL_DIR / model_name
        if not model_path.exists():
            print(f"Skipping '{model_name}': file does not exist locally at {model_path}.")
            continue

        print(f"Uploading '{model_name}' ({os.path.getsize(model_path) / (1024*1024):.2f} MB)...")
        try:
            with open(model_path, "rb") as f:
                upload_file(f.read(), model_name, container_name="models")
            print(f"Successfully uploaded '{model_name}' to Azure Blob Storage.")
        except Exception as e:
            print(f"Error uploading '{model_name}': {e}")


if __name__ == "__main__":
    main()
