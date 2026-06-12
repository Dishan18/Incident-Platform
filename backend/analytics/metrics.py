"""
Core KPI and metric calculations for incident analytics.
All functions are pure: they accept a DataFrame and return results
without side effects.
"""

import pandas as pd


def get_kpis(df: pd.DataFrame) -> dict:
    """Calculate key performance indicators from incident data.

    Returns
    -------
    dict
        Keys: ``total``, ``open``, ``resolved``, ``avg_resolution_time``,
        ``critical_count``, ``app_count``.
    """
    total = len(df)

    open_statuses = {"Open", "Assigned", "In Progress"}
    resolved_statuses = {"Resolved", "Closed"}

    open_count = int(df["status"].isin(open_statuses).sum())
    resolved_count = int(df["status"].isin(resolved_statuses).sum())

    resolution_times = pd.to_numeric(
        df["resolution_time"], errors="coerce"
    ).dropna()
    avg_resolution = (
        round(float(resolution_times.mean()), 1)
        if not resolution_times.empty
        else 0.0
    )

    critical_count = int((df["priority"] == "P1").sum())
    app_count = int(df["application"].nunique())

    return {
        "total": total,
        "open": open_count,
        "resolved": resolved_count,
        "avg_resolution_time": avg_resolution,
        "critical_count": critical_count,
        "app_count": app_count,
    }


def get_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly incident counts as a two-column DataFrame."""
    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])
    df["month"] = df["created_at"].dt.to_period("M").astype(str)
    trend = df.groupby("month").size().reset_index(name="count")
    return trend.sort_values("month").reset_index(drop=True)


def get_resolution_time_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly average resolution times."""
    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["resolution_time"] = pd.to_numeric(df["resolution_time"], errors="coerce")
    df = df.dropna(subset=["created_at", "resolution_time"])
    df["month"] = df["created_at"].dt.to_period("M").astype(str)
    trend = df.groupby("month")["resolution_time"].mean().reset_index()
    trend.columns = ["month", "avg_resolution_time"]
    trend["avg_resolution_time"] = trend["avg_resolution_time"].round(1)
    return trend.sort_values("month").reset_index(drop=True)
