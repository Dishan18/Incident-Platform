"""
Table and incident detail view components.
"""

import pandas as pd
import streamlit as st

from frontend.components.cards import render_priority_badge, render_status_badge
from frontend.styles.theme import TEXT, MUTED, ACCENT


def render_data_table(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> None:
    """Render a styled data table using ``st.dataframe``."""
    display = df[columns] if columns else df
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_incident_detail(incident: dict) -> None:
    """Render the incident detail drawer with lifecycle timeline and status controls.

    Displays all incident fields, a visual lifecycle timeline showing
    which stages have been completed, and a status-update dropdown
    restricted to valid ITSM transitions.
    """
    inc_id = incident.get("incident_id", "")
    status = str(incident.get("status", ""))
    priority = str(incident.get("priority", ""))

    priority_badge = render_priority_badge(priority)
    status_badge = render_status_badge(status)

    # ── Header ──
    st.markdown(
        f'<div style="font-size:16px; font-weight:600; color:{TEXT};'
        f' margin-bottom:16px;">{inc_id}</div>'
        f'<div style="margin-bottom:20px; display:flex; gap:8px;">'
        f"{priority_badge} {status_badge}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Fields ──
    fields = [
        ("Description", incident.get("description", "")),
        ("Application", incident.get("application", "")),
        ("Category", incident.get("category", "")),
        ("Affected Users", str(incident.get("affected_users", ""))),
        ("Impact Scope", incident.get("impact_scope", "")),
        ("Environment", incident.get("environment", "")),
        ("Teams", incident.get("teams", "")),
    ]

    for label, value in fields:
        st.markdown(
            f'<div class="detail-label">{label}</div>'
            f'<div class="detail-value">{value}</div>',
            unsafe_allow_html=True,
        )

    # ── Lifecycle Timeline ──
    st.markdown(
        f'<div style="margin-top:24px; font-size:14px; font-weight:600;'
        f' color:{TEXT}; margin-bottom:12px;">Lifecycle Timeline</div>',
        unsafe_allow_html=True,
    )

    timeline_steps = [
        ("Created", incident.get("created_at", "")),
        ("Assigned", incident.get("assigned_at", "")),
        ("In Progress", incident.get("in_progress_at", "")),
        ("Resolved", incident.get("resolved_at", "")),
        ("Closed", incident.get("closed_at", "")),
    ]

    for step_label, timestamp in timeline_steps:
        has_time = bool(
            timestamp
            and str(timestamp) not in ("", "nan", "NaT", "None")
            and not (isinstance(timestamp, float) and pd.isna(timestamp))
        )
        dot_class = "completed" if has_time else "pending"
        label_class = "" if has_time else "pending"
        time_display = str(timestamp)[:19] if has_time else ""
        time_html = (
            f'<div class="timeline-step-time">{time_display}</div>'
            if has_time
            else ""
        )

        st.markdown(
            f"""
            <div class="timeline-step">
                <div class="timeline-dot {dot_class}"></div>
                <div>
                    <div class="timeline-step-label {label_class}">{step_label}</div>
                    {time_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Status Update ──
    from backend.incident.update_incident import (
        get_valid_transitions,
        update_incident_status,
    )

    valid_next = get_valid_transitions(status)
    if valid_next:
        st.markdown(
            f'<div style="margin-top:24px; font-size:14px; font-weight:600;'
            f' color:{TEXT}; margin-bottom:8px;">Update Status</div>',
            unsafe_allow_html=True,
        )

        new_status = st.selectbox(
            "New Status",
            valid_next,
            key=f"status_sel_{inc_id}",
            label_visibility="collapsed",
        )

        if st.button("Update Status", key=f"update_btn_{inc_id}"):
            success, message = update_incident_status(inc_id, new_status)
            if success:
                st.toast(f"{inc_id} status updated to {new_status}.")
                st.rerun()
            else:
                st.error(message)
    else:
        st.markdown(
            f'<div style="margin-top:16px; color:{MUTED}; font-size:13px;">'
            f"This incident is in a terminal state ({status})."
            f"</div>",
            unsafe_allow_html=True,
        )
