import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv("D:\TicketingPlatform\data\synthetic_tickets.csv")

df["primary_team"] = (
    df["teams"]
    .str.split(",")
    .str[0]
)

X = df["description"]
y = df["primary_team"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            max_features=5000
        )
    ),
    (
        "clf",
        LogisticRegression(
            max_iter=2000
        )
    )
])

model.fit(X_train, y_train)

preds = model.predict(X_test)

print(classification_report(y_test, preds))

joblib.dump(
    model,
    "models/team_model.pkl",
    compress=3
)
print("Model saved.")

try:
    from backend.cloud.azure_blob import upload_file
    with open("models/team_model.pkl", "rb") as f:
        upload_file(f.read(), "team_model.pkl", container_name="models")
    print("team_model.pkl successfully uploaded to Azure Blob Storage container 'models'.")
except Exception as e:
    print(f"Failed to upload team_model.pkl to Azure Storage: {e}")