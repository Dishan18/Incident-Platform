"""
Filter components for the Analytics page.
Renders filter controls and applies selections to DataFrames.
"""

from typing import Dict, Tuple

import pandas as pd
import streamlit as st


def render_filters(df: pd.DataFrame) -> dict:
    """Render a row of filter controls and return the selected values.

    Returns
    -------
    dict
        Keys: ``date_range``, ``priority``, ``application``,
        ``team``, ``status``.
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        dates = pd.to_datetime(df["created_at"], errors="coerce").dropna()
        min_date = dates.min().date() if not dates.empty else pd.Timestamp("2025-01-01").date()
        max_date = dates.max().date() if not dates.empty else pd.Timestamp.now().date()
        date_range: Tuple = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with col2:
        priorities = ["All"] + sorted(
            df["priority"].dropna().unique().tolist()
        )
        selected_priority = st.selectbox("Priority", priorities)

    with col3:
        applications = ["All"] + sorted(
            df["application"].dropna().unique().tolist()
        )
        selected_app = st.selectbox("Application", applications)

    with col4:
        preferred_order = ["Unix/Linux", "Wintel", "Batch", "Middleware", "Network", "Database"]
        all_teams: set[str] = set()
        for teams_str in df["teams"].dropna():
            for t in str(teams_str).split(","):
                if t.strip():
                    all_teams.add(t.strip())
        all_teams = all_teams.union(preferred_order)
        teams_list = [t for t in preferred_order if t in all_teams] + sorted(list(all_teams - set(preferred_order)))
        selected_teams = st.multiselect("Teams", teams_list)

    with col5:
        statuses = ["All"] + sorted(
            df["status"].dropna().unique().tolist()
        )
        selected_status = st.selectbox("Status", statuses)

    return {
        "date_range": date_range,
        "priority": selected_priority,
        "application": selected_app,
        "team": selected_teams,
        "status": selected_status,
    }


def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply the filter dict returned by ``render_filters`` to *df*."""
    filtered = df.copy()
    filtered["created_at"] = pd.to_datetime(
        filtered["created_at"], errors="coerce"
    )

    # Date range
    date_range = filters.get("date_range")
    if date_range and len(date_range) == 2:
        start, end = date_range
        mask = (filtered["created_at"].dt.date >= start) & (
            filtered["created_at"].dt.date <= end
        )
        filtered = filtered[mask]

    # Categorical filters
    if filters.get("priority") and filters["priority"] != "All":
        filtered = filtered[filtered["priority"] == filters["priority"]]

    if filters.get("application") and filters["application"] != "All":
        filtered = filtered[
            filtered["application"] == filters["application"]
        ]

    selected_teams = filters.get("team")
    if selected_teams:
        def matches_any_team(teams_str):
            if pd.isna(teams_str) or not str(teams_str).strip():
                return False
            incident_teams = {t.strip() for t in str(teams_str).split(",") if t.strip()}
            return not incident_teams.isdisjoint(selected_teams)
            
        filtered = filtered[filtered["teams"].apply(matches_any_team)]

    if filters.get("status") and filters["status"] != "All":
        filtered = filtered[filtered["status"] == filters["status"]]

    return filtered
