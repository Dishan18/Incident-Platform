"""
Incidents page -- Core workflow with timeline and incident management.

Provides incident creation via modal dialog, a date-grouped timeline
view of live incidents, and a detail drawer with status-update controls.
"""

import streamlit as st

from backend.incident.create_incident import APP_TEAM_MAP, create_incident
from backend.incident.incident_repository import (
    get_incident_by_id,
    get_incidents_grouped_by_date,
)
from frontend.components.tables import render_incident_detail
from frontend.components.timeline import render_timeline
from frontend.styles.theme import MUTED, TEXT


# ── Dialog ──

@st.dialog("Create New Incident", width="large")
def _new_incident_dialog() -> None:
    """Modal dialog for creating a new incident."""
    description = st.text_area(
        "Description",
        placeholder="Describe the incident symptoms and impact...",
        height=100,
    )

    applications = sorted(APP_TEAM_MAP.keys())
    application = st.selectbox("Application", applications)

    col_a, col_b = st.columns(2)
    with col_a:
        affected_users = st.number_input(
            "Affected Users", min_value=1, value=1, step=1
        )
    with col_b:
        impact_scope = st.selectbox(
            "Impact Scope",
            ["single_user", "department", "site", "enterprise"],
        )

    environment = st.selectbox(
        "Environment", ["Production", "UAT", "Development"]
    )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    if st.button("Submit Incident", use_container_width=True):
        if not description.strip():
            st.error("Description is required.")
            return

        incident = create_incident(
            description=description.strip(),
            application=application,
            affected_users=int(affected_users),
            impact_scope=impact_scope,
            environment=environment,
        )
        st.toast(f"Incident {incident['incident_id']} created.")
        st.rerun()


# ── Page ──

def render_incidents() -> None:
    """Render the Incidents management page."""
    # Header row
    col_title, col_btn = st.columns([0.8, 0.2])
    with col_title:
        st.markdown(
            f'<div style="font-size:20px; font-weight:600; color:{TEXT};">'
            f"Incidents</div>"
            f'<div style="font-size:14px; color:{MUTED}; margin-top:4px;">'
            f"Manage and track operational incidents</div>",
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button("+ New Incident", use_container_width=True):
            _new_incident_dialog()

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # Layout: Timeline (left) + Detail (right)
    selected_id = st.session_state.get("selected_incident_id")

    col_timeline, col_detail = st.columns([0.55, 0.45])

    with col_timeline:
        incidents_by_date = get_incidents_grouped_by_date()
        render_timeline(incidents_by_date)

    with col_detail:
        if selected_id:
            # Close button
            if st.button("Close", key="close_detail"):
                del st.session_state["selected_incident_id"]
                st.rerun()

            incident = get_incident_by_id(selected_id)
            if incident:
                render_incident_detail(incident)
            else:
                st.warning(f"Incident {selected_id} not found.")
                del st.session_state["selected_incident_id"]
        else:
            st.markdown(
                '<div class="empty-state">'
                "Select an incident from the timeline to view details."
                "</div>",
                unsafe_allow_html=True,
            )
