import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv(
    "data/synthetic_tickets.csv"
)

X = df[
    [
        "description",
        "application",
        "affected_users",
        "impact_scope"
    ]
]

y = df["priority"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "text",
            TfidfVectorizer(
                max_features=5000
            ),
            "description"
        ),
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            [
                "application",
                "impact_scope"
            ]
        ),
        (
            "num",
            "passthrough",
            [
                "affected_users"
            ]
        )
    ]
)

model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "classifier",
        RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        )
    )
])

model.fit(
    X_train,
    y_train
)

preds = model.predict(
    X_test
)

print(
    classification_report(
        y_test,
        preds
    )
)

joblib.dump(
    model,
    "models/priority_model.pkl"
)

print(
    "priority_model.pkl saved"
)