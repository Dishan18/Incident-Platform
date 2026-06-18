import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = "data/synthetic_tickets.csv"


def clean_text(text: str) -> str:
    """Normalize and clean incident descriptions for more robust similarity mapping."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Normalize common ticketing synonyms & prefixes
    text = re.sub(r"\b(cant|can't|cannot)\b", "cannot", text)
    text = re.sub(r"\b(log\s+in|log\s+into|login|logon|log\s+on)\b", "log", text)
    text = re.sub(r"\b(database|db)\b", "database", text)
    text = re.sub(r"\b(credentials|credential|creds)\b", "credential", text)
    text = re.sub(r"\b(connections|connected|connecting|connection|connects|connect)\b", "connect", text)
    text = re.sub(r"\b(failures|failing|failed|fails|failure)\b", "fail", text)
    text = re.sub(r"\b(servers|server)\b", "server", text)
    text = re.sub(r"\b(users|user)\b", "user", text)
    text = re.sub(r"\b(observed|observe|observing)\b", "observe", text)
    text = re.sub(r"\b(issues|issue)\b", "issue", text)
    text = re.sub(r"\b(outages|outage)\b", "outage", text)
    text = re.sub(r"\b(errors|error)\b", "error", text)
    
    # Strip non-alphanumeric (keep spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


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

    cleaned_descriptions = [clean_text(d) for d in descriptions]
    cleaned_query = clean_text(description)
    corpus = cleaned_descriptions + [cleaned_query]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        use_idf=False
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