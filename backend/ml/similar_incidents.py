import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = "data/synthetic_tickets.csv"


def get_similar_incidents(
    description: str,
    top_k: int = 5
):
    df = pd.read_csv(DATA_PATH)

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

        output.append({
            "description":
                row["description"],

            "team":
                row["teams"],

            "priority":
                row["priority"],

            "resolution_time":
                row["resolution_time"],

            "root_cause":
                row["root_cause"],

            "similarity":
                round(
                    row["similarity"] * 100,
                    2
                )
        })

    return output