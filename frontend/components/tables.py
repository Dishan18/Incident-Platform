"""
Incident detail view component.
"""

import pandas as pd
import streamlit as st

from frontend.components.cards import render_priority_badge, render_status_badge
from frontend.styles.theme import TEXT, MUTED


def render_incident_detail(incident: dict) -> None:
    """Render the incident detail drawer with lifecycle timeline and status controls.

    Displays all incident fields, a visual lifecycle timeline showing
    which stages have been completed, and direct status-update action
    buttons for valid ITSM transitions.
    """
    inc_id = incident.get("incident_id", "")
    status = str(incident.get("status", ""))
    priority = str(incident.get("priority", ""))

    priority_badge = render_priority_badge(priority)
    status_badge = render_status_badge(status)

    # ── Header ──
    st.markdown(
        f'<div class="detail-header-id">{inc_id}</div>'
        f'<div style="margin-bottom:20px; display:flex; gap:8px;">'
        f"{priority_badge} {status_badge}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Fields ──
    # Description full-width
    st.markdown(
        f'<div class="detail-label">Description</div>'
        f'<div class="detail-value">{incident.get("description", "")}</div>',
        unsafe_allow_html=True,
    )

    # Metadata Grid (2 Columns)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="detail-label">Application</div>'
            f'<div class="detail-value">{incident.get("application", "")}</div>'
            f'<div class="detail-label">Category</div>'
            f'<div class="detail-value">{incident.get("category", "")}</div>'
            f'<div class="detail-label">Affected Users</div>'
            f'<div class="detail-value">{incident.get("affected_users", "")}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="detail-label">Assigned Team</div>'
            f'<div class="detail-value">{incident.get("teams", "")}</div>'
            f'<div class="detail-label">Environment</div>'
            f'<div class="detail-value">{incident.get("environment", "")}</div>'
            f'<div class="detail-label">Impact Scope</div>'
            f'<div class="detail-value">{incident.get("impact_scope", "").replace("_", " ").title()}</div>',
            unsafe_allow_html=True,
        )

    # ── Lifecycle Timeline ──
    st.markdown(
        '<div class="detail-section-title">Lifecycle Timeline</div>',
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
            f'<div class="timeline-step">'
            f'<div class="timeline-dot {dot_class}"></div>'
            f'<div>'
            f'<div class="timeline-step-label {label_class}">{step_label}</div>'
            f'{time_html}'
            f'</div>'
            f'</div>',
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
            '<div class="detail-section-title">Update Status</div>',
            unsafe_allow_html=True,
        )

        # Create horizontal action buttons for each valid next status
        cols = st.columns(len(valid_next))
        label_map = {
            "Assigned": "Assign",
            "In Progress": "Start Progress",
            "Resolved": "Resolve",
            "Closed": "Close",
            "Cancelled": "Cancel",
        }
        for col, next_status in zip(cols, valid_next):
            button_label = label_map.get(next_status, next_status)
            with col:
                if st.button(button_label, key=f"update_btn_{inc_id}_{next_status}", use_container_width=True):
                    success, message = update_incident_status(inc_id, next_status)
                    if success:
                        st.toast(f"{inc_id} status updated to {next_status}.")
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
