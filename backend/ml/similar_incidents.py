import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = "data/synthetic_tickets.csv"


def get_similar_incidents(
    description: str,
    top_k: int = 5,
    active_only: bool = False
):
    if active_only:
        from backend.utils.data_loader import load_live_incidents
        df = load_live_incidents()
        if df.empty:
            return []
        # Filter for active incidents only (status NOT IN ('Closed', 'Cancelled'))
        df = df[~df["status"].isin(["Closed", "Cancelled"])].copy()
        if df.empty:
            return []
    else:
        df = pd.read_csv(DATA_PATH)
        # For historical data, rename ticket_id to incident_id to match common schema
        df = df.rename(columns={"ticket_id": "incident_id"})

    descriptions = (
        df["description"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    corpus = descriptions + [description]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf = vectorizer.fit_transform(
        corpus
    )

    query_vector = tfidf[-1]
    historical_vectors = tfidf[:-1]

    similarities = cosine_similarity(
        query_vector,
        historical_vectors
    )[0]

    df["similarity"] = similarities

    if active_only:
        results = (
            df.sort_values(
                "similarity",
                ascending=False
            )
            .head(top_k)
        )
    else:
        results = (
            df.sort_values(
                "similarity",
                ascending=False
            )
            .drop_duplicates(
                subset=["description", "root_cause"]
            )
            .head(top_k)
        )

    output = []

    for _, row in results.iterrows():
        # format created_at safely
        created_val = row.get("created_at")
        if pd.notna(created_val):
            if hasattr(created_val, "strftime"):
                created_str = created_val.strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_str = str(created_val)
        else:
            created_str = ""

        output.append({
            "incident_id":
                row.get("incident_id", ""),

            "description":
                row["description"],

            "team":
                row.get("teams", ""),

            "priority":
                row["priority"],

            "resolution_time":
                row.get("resolution_time", ""),

            "root_cause":
                row.get("root_cause", ""),

            "status":
                row.get("status", ""),

            "created_at":
                created_str,

            "similarity":
                round(
                    row["similarity"] * 100,
                    2
                )
        })

    return output