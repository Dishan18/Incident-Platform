"""
Incident detail view component with editing/saving controls.
"""

import pandas as pd
import streamlit as st

from frontend.components.cards import render_priority_badge, render_status_badge
from frontend.styles.theme import TEXT, MUTED


def _update_incident_details(
    incident_id: str,
    team: str,
    priority: str,
    root_cause: str,
    resolution_time: int | None = None,
) -> bool:
    """Save manually updated operational fields back to the SQLite database."""
    from backend.database.incident_repository import get_incident as db_get_incident
    from backend.database.incident_repository import update_overrides as db_update_overrides

    inc = db_get_incident(incident_id)
    if not inc:
        return False

    team_overridden = inc.ai_predicted_team != team
    priority_overridden = inc.ai_predicted_priority != priority

    return db_update_overrides(
        incident_id=incident_id,
        team=team,
        priority=priority,
        root_cause=root_cause,
        team_overridden=team_overridden,
        priority_overridden=priority_overridden,
        resolution_time=resolution_time,
    )


def render_incident_detail(incident: dict) -> None:
    """Render the incident detail drawer with lifecycle timeline and status controls.

    Supports dual-mode rendering: a default read-only detail panel, and an
    editable settings form to modify team routing, priority, actual root cause,
    and actual resolution duration if the incident is resolved or closed.
    """
    inc_id = incident.get("incident_id", "")
    status = str(incident.get("status", ""))
    priority = str(incident.get("priority", ""))

    priority_badge = render_priority_badge(priority)
    status_badge = render_status_badge(status)

    # ── Edit Mode State ──
    edit_mode = st.session_state.get(f"edit_mode_{inc_id}", False)

    # ── Header ──
    col_header, col_edit_btn = st.columns([0.75, 0.25])
    with col_header:
        st.markdown(
            f'<div class="detail-header-id">{inc_id}</div>'
            f'<div style="margin-bottom:20px; display:flex; gap:8px;">'
            f"{priority_badge} {status_badge}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_edit_btn:
        if not edit_mode:
            if st.button("Edit", key=f"edit_btn_{inc_id}", use_container_width=True):
                st.session_state[f"edit_mode_{inc_id}"] = True
                st.rerun()

    # ── Check Resolution Time Metadata ──
    res_time = incident.get("resolution_time", "")
    has_res_time = (
        res_time not in ("", "nan", "NaT", "None")
        and not (isinstance(res_time, float) and pd.isna(res_time))
    )

    if edit_mode:
        # ── EDIT VIEW ──
        st.markdown(
            f'<div class="detail-label">Description</div>'
            f'<div class="detail-value">{incident.get("description", "")}</div>',
            unsafe_allow_html=True,
        )

        # Static Metadata Column
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            st.markdown(
                f'<div class="detail-label">Application</div>'
                f'<div class="detail-value">{incident.get("application", "")}</div>'
                f'<div class="detail-label">Category</div>'
                f'<div class="detail-value">{incident.get("category", "")}</div>',
                unsafe_allow_html=True,
            )
        with col_meta2:
            st.markdown(
                f'<div class="detail-label">Environment</div>'
                f'<div class="detail-value">{incident.get("environment", "")}</div>'
                f'<div class="detail-label">Impact Scope</div>'
                f'<div class="detail-value">{incident.get("impact_scope", "").replace("_", " ").title()}</div>',
                unsafe_allow_html=True,
            )

        # Editable Fields
        all_teams = ["Unix/Linux", "Wintel", "Batch", "Middleware", "Network", "Database"]
        current_team = incident.get("teams", "")
        current_teams_list = [t.strip() for t in current_team.split(",") if t.strip()]
        selected_teams = st.multiselect(
            "Assigned Teams",
            all_teams,
            default=[t for t in current_teams_list if t in all_teams],
            key=f"edit_team_sel_{inc_id}",
        )

        all_priorities = ["P1", "P2", "P3", "P4"]
        current_priority = incident.get("priority", "")
        selected_priority = st.selectbox(
            "Priority Level",
            all_priorities,
            index=all_priorities.index(current_priority) if current_priority in all_priorities else 0,
            key=f"edit_priority_sel_{inc_id}",
        )

        typed_root_cause = st.text_area(
            "Root Cause",
            value=incident.get("root_cause", ""),
            key=f"edit_rc_area_{inc_id}",
        )

        # Resolution Time is mutable only if it is already stored or if status is resolved/closed
        show_res_time_input = has_res_time or status in ("Resolved", "Closed")
        edited_res_time = None

        if show_res_time_input:
            default_val = int(float(res_time)) if has_res_time else 0
            edited_res_time = st.number_input(
                "Actual Resolution Time (minutes)",
                min_value=0,
                value=default_val,
                step=1,
                key=f"edit_res_time_num_{inc_id}",
            )

        vertical_spacer_val = 24
        st.markdown(f'<div style="height:{vertical_spacer_val}px;"></div>', unsafe_allow_html=True)

        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("Save Changes", key=f"save_btn_{inc_id}", use_container_width=True):
                res_val = int(edited_res_time) if show_res_time_input else (int(float(res_time)) if has_res_time else None)
                success = _update_incident_details(
                    incident_id=inc_id,
                    team=", ".join(selected_teams),
                    priority=selected_priority,
                    root_cause=typed_root_cause,
                    resolution_time=res_val,
                )
                if success:
                    st.session_state[f"edit_mode_{inc_id}"] = False
                    st.toast("Incident details saved successfully.")
                    st.rerun()
                else:
                    st.error("Failed to update incident details.")

        with col_cancel:
            if st.button("Cancel", key=f"cancel_btn_{inc_id}", use_container_width=True):
                st.session_state[f"edit_mode_{inc_id}"] = False
                st.rerun()

    else:
        # ── READ-ONLY VIEW ──
        st.markdown(
            f'<div class="detail-label">Description</div>'
            f'<div class="detail-value">{incident.get("description", "")}</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div class="detail-label">Application</div>'
                f'<div class="detail-value">{incident.get("application", "")}</div>'
                f'<div class="detail-label">Category</div>'
                f'<div class="detail-value">{incident.get("category", "")}</div>'
                f'<div class="detail-label">Affected Users</div>'
                f'<div class="detail-value">{int(float(incident.get("affected_users", 1)))}</div>',
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

        st.markdown(
            f'<div class="detail-label">Root Cause</div>'
            f'<div class="detail-value">{incident.get("root_cause", "") or "Not specified"}</div>',
            unsafe_allow_html=True,
        )

        if has_res_time:
            st.markdown(
                f'<div class="detail-label">Actual Resolution Time</div>'
                f'<div class="detail-value">{int(float(res_time))} min</div>',
                unsafe_allow_html=True,
            )

        # ── Lifecycle Timeline (only visible when not editing) ──
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

        # ── Status Update Actions (only visible when not editing) ──
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
