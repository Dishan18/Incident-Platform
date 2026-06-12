"""
Trend and distribution analytics for incident data.
"""

import pandas as pd


def get_priority_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return incident counts by priority level, ordered P1-P4."""
    dist = df["priority"].value_counts().reset_index()
    dist.columns = ["priority", "count"]
    priority_order = ["P1", "P2", "P3", "P4"]
    dist["priority"] = pd.Categorical(
        dist["priority"], categories=priority_order, ordered=True
    )
    return dist.sort_values("priority").reset_index(drop=True)


def get_priority_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly incident counts broken down by priority."""
    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])
    df["month"] = df["created_at"].dt.to_period("M").astype(str)
    trend = df.groupby(["month", "priority"]).size().reset_index(name="count")
    return trend.sort_values("month").reset_index(drop=True)


def get_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return incident counts by status."""
    dist = df["status"].value_counts().reset_index()
    dist.columns = ["status", "count"]
    return dist
