"""
Root cause analysis functions.
Provides distributions for treemaps, stacked bars, and box plots.
"""

import pandas as pd


def get_root_cause_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return root cause counts for treemap / bar visualisation."""
    if "root_cause" not in df.columns:
        return pd.DataFrame(columns=["root_cause", "count"])

    dist = df["root_cause"].dropna().value_counts().reset_index()
    dist.columns = ["root_cause", "count"]
    return dist


def get_root_cause_by_team(df: pd.DataFrame) -> pd.DataFrame:
    """Return root cause distribution broken down by team.

    Each row in the result has ``team``, ``root_cause``, and ``count``.
    Used for treemap visualisation with team -> root_cause hierarchy.
    """
    rows: list[dict] = []
    for _, row in df.iterrows():
        if pd.isna(row.get("teams")) or pd.isna(row.get("root_cause")):
            continue
        for team in str(row["teams"]).split(","):
            rows.append({
                "team": team.strip(),
                "root_cause": str(row["root_cause"]),
            })

    if not rows:
        return pd.DataFrame(columns=["team", "root_cause", "count"])

    result = pd.DataFrame(rows)
    return (
        result.groupby(["team", "root_cause"])
        .size()
        .reset_index(name="count")
    )


def get_resolution_by_priority(df: pd.DataFrame) -> pd.DataFrame:
    """Return resolution times with priority labels for box plots."""
    df = df.copy()
    df["resolution_time"] = pd.to_numeric(df["resolution_time"], errors="coerce")
    return df.dropna(subset=["resolution_time"])[
        ["priority", "resolution_time"]
    ].reset_index(drop=True)
