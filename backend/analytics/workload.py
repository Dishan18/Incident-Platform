"""
Team workload and application analytics.
Handles comma-separated team assignments in the ``teams`` column.
"""

from typing import List

import pandas as pd


def get_team_workload(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate incident counts per team (handles multi-team assignments)."""
    teams_series = df["teams"].dropna().str.split(",")
    all_teams: List[str] = []
    for team_list in teams_series:
        all_teams.extend(t.strip() for t in team_list)

    team_counts = pd.Series(all_teams).value_counts().reset_index()
    team_counts.columns = ["team", "count"]
    return team_counts.sort_values("count", ascending=True).reset_index(drop=True)


def get_top_applications(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top *n* applications by incident volume."""
    app_counts = df["application"].value_counts().head(n).reset_index()
    app_counts.columns = ["application", "count"]
    return app_counts


def get_team_priority_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Build a team-vs-priority pivot table for heatmap charts.

    Returns a DataFrame indexed by team with columns P1-P4.
    """
    rows: list[dict] = []
    for _, row in df.iterrows():
        if pd.isna(row.get("teams")):
            continue
        for team in str(row["teams"]).split(","):
            rows.append({"team": team.strip(), "priority": row["priority"]})

    if not rows:
        return pd.DataFrame()

    expanded = pd.DataFrame(rows)
    pivot = (
        expanded.groupby(["team", "priority"])
        .size()
        .reset_index(name="count")
        .pivot(index="team", columns="priority", values="count")
        .fillna(0)
    )

    for p in ["P1", "P2", "P3", "P4"]:
        if p not in pivot.columns:
            pivot[p] = 0
    return pivot[["P1", "P2", "P3", "P4"]]
