"""
Incidents page -- Core workflow with timeline and incident management.

Provides incident creation via modal dialog, a date-grouped timeline
view of live incidents with filtering capabilities, and a detail drawer.
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

from backend.incident.create_incident import APP_TEAM_MAP, create_incident
from backend.incident.incident_repository import (
    get_incident_by_id,
    get_live_incidents,
)
from frontend.components.tables import render_incident_detail
from frontend.components.timeline import render_timeline
from frontend.styles.theme import vertical_spacer


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

    vertical_spacer(12)

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


def render_incidents() -> None:
    """Render the Incidents management page."""
    # Header row with title on left and "+ New Incident" button on right
    col_title, col_btn = st.columns([0.8, 0.2])
    with col_title:
        st.markdown(
            """
            <div class="page-header-container" style="border-bottom: none; margin-bottom: 0px; padding-bottom: 0px;">
                <div class="page-header-title">Incidents</div>
                <div class="page-header-subtitle">Manage and track operational incidents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_btn:
        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        if st.button("+ New Incident", use_container_width=True):
            _new_incident_dialog()

    # Consistent border-bottom separator matching the page header container
    st.markdown('<hr style="margin-top:0px; margin-bottom:16px;">', unsafe_allow_html=True)

    # ── Filters Bar ──
    live_df = get_live_incidents()
    today_date = datetime.now().date()

    with st.container():
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            status_opts = ["All", "Open", "Assigned", "In Progress", "Resolved", "Closed", "Cancelled"]
            selected_status = st.selectbox("Status", status_opts, key="inc_filter_status")

        with col_f2:
            priority_opts = ["All", "P1", "P2", "P3", "P4"]
            selected_priority = st.selectbox("Priority", priority_opts, key="inc_filter_priority")

        with col_f3:
            app_opts = ["All"] + sorted(APP_TEAM_MAP.keys())
            selected_app = st.selectbox("Application", app_opts, key="inc_filter_app")

        with col_f4:
            # Default to showing Today's incidents only
            selected_date_range = st.date_input(
                "Date Range",
                value=(today_date, today_date),
                key="inc_filter_dates",
            )

    vertical_spacer(20)

    # ── Apply Filters ──
    filtered_df = live_df.copy() if not live_df.empty else pd.DataFrame()
    if not filtered_df.empty:
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df["status"] == selected_status]

        if selected_priority != "All":
            filtered_df = filtered_df[filtered_df["priority"] == selected_priority]

        if selected_app != "All":
            filtered_df = filtered_df[filtered_df["application"] == selected_app]

        if selected_date_range:
            if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
                start_d, end_d = selected_date_range
                filtered_df = filtered_df[
                    (filtered_df["created_at"].dt.date >= start_d) &
                    (filtered_df["created_at"].dt.date <= end_d)
                ]
            elif isinstance(selected_date_range, tuple) and len(selected_date_range) == 1:
                start_d = selected_date_range[0]
                filtered_df = filtered_df[filtered_df["created_at"].dt.date == start_d]
            else:
                filtered_df = filtered_df[filtered_df["created_at"].dt.date == selected_date_range]

    # ── Group Incidents by Date for Timeline ──
    groups = {}
    if not filtered_df.empty:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Ensure correct chronological order (newest first)
        filtered_df = filtered_df.sort_values("created_at", ascending=False)
        
        for _, row in filtered_df.iterrows():
            created = row["created_at"]
            if pd.isna(created):
                continue
                
            incident_date = created.date()
            if incident_date == today:
                label = "Today"
            elif incident_date == yesterday:
                label = "Yesterday"
            else:
                label = incident_date.strftime("%B %d, %Y")
                
            if label not in groups:
                groups[label] = []
            groups[label].append(row.to_dict())

    # Layout: Timeline (left) + Detail (right)
    selected_id = st.session_state.get("selected_incident_id")

    col_timeline, col_detail = st.columns([0.55, 0.45])

    with col_timeline:
        render_timeline(groups)

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
