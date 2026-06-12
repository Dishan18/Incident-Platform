import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv(
    "data/synthetic_tickets.csv"
)

df["primary_team"] = (
    df["teams"]
    .str.split(",")
    .str[0]
)

X = df[
    [
        "description",
        "application",
        "priority",
        "primary_team",
        "affected_users",
        "impact_scope"
    ]
]

y = df["resolution_time"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
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
                "priority",
                "primary_team",
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
        "regressor",
        RandomForestRegressor(
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
    "MAE:",
    mean_absolute_error(
        y_test,
        preds
    )
)

print(
    "R2:",
    r2_score(
        y_test,
        preds
    )
)

joblib.dump(
    model,
    "models/resolution_model.pkl"
)

print(
    "resolution_model.pkl saved"
)