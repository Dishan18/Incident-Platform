"""
Predictions page -- Incident Intelligence Center.
"""

import pandas as pd
import streamlit as st

from backend.ml.predict_incident import predict_incident
from backend.ml.similar_incidents import get_similar_incidents
from backend.incident.create_incident import APP_TEAM_MAP
from backend.utils.data_loader import load_live_incidents

from frontend.components.cards import render_prediction_card, render_priority_badge, render_status_badge
from frontend.styles.theme import render_page_header, vertical_spacer
from backend.ml.explain_prediction import explain_prediction


def render_predictions() -> None:
    """Render the Predictions page as an Incident Intelligence Center."""
    # ── Page Header ──
    render_page_header(
        "Predictions",
        "Incident Intelligence Center: Real-time ML routing, priority, and similarity triage",
    )

    vertical_spacer(24)

    # Load live incidents
    live_df = load_live_incidents()

    col_left, col_spacer, col_right = st.columns([0.42, 0.04, 0.54])

    with col_left:
        st.markdown(
            '<div class="section-title" style="margin-top:0;">Filters</div>',
            unsafe_allow_html=True,
        )

        # ── Filters ──
        status_options = ["All", "Open", "Assigned", "In Progress", "Resolved", "Closed", "Cancelled"]
        selected_status = st.selectbox("Status", status_options, key="pred_filter_status")

        priority_options = ["All", "P1", "P2", "P3", "P4"]
        selected_priority = st.selectbox("Priority", priority_options, key="pred_filter_priority")

        app_options = ["All"] + sorted(APP_TEAM_MAP.keys())
        selected_app = st.selectbox("Application", app_options, key="pred_filter_app")

        # Dynamic Date Range based on live incidents
        if not live_df.empty:
            live_df["created_at_dt"] = pd.to_datetime(live_df["created_at"])
            min_date = live_df["created_at_dt"].min().date()
            max_date = live_df["created_at_dt"].max().date()
        else:
            min_date = pd.Timestamp("2026-01-01").date()
            max_date = pd.Timestamp.now().date()

        if min_date == max_date:
            min_date = min_date - pd.Timedelta(days=7)

        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date - pd.Timedelta(days=365),
            max_value=max_date + pd.Timedelta(days=30),
            key="pred_filter_dates",
        )

        vertical_spacer(24)

        st.markdown(
            '<div class="section-title">Incident List</div>',
            unsafe_allow_html=True,
        )

        # ── Filter Incidents ──
        filtered_live = live_df.copy() if not live_df.empty else pd.DataFrame()
        if not filtered_live.empty:
            if selected_status != "All":
                filtered_live = filtered_live[filtered_live["status"] == selected_status]

            if selected_priority != "All":
                filtered_live = filtered_live[filtered_live["priority"] == selected_priority]

            if selected_app != "All":
                filtered_live = filtered_live[filtered_live["application"] == selected_app]

            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                filtered_live = filtered_live[
                    (filtered_live["created_at_dt"].dt.date >= start_date) &
                    (filtered_live["created_at_dt"].dt.date <= end_date)
                ]

        # ── Render Incident Selector List ──
        if filtered_live.empty:
            st.markdown(
                '<div class="empty-state">No incidents match the selected filters.</div>',
                unsafe_allow_html=True,
            )
        else:
            for _, row in filtered_live.iterrows():
                iid = row["incident_id"]
                desc = row["description"]
                status = row["status"]
                priority = row["priority"]

                priority_html = render_priority_badge(priority)
                status_html = render_status_badge(status)

                # Row columns
                col_info, col_btn = st.columns([0.76, 0.24])

                with col_info:
                    st.markdown(
                        f'<div class="incident-card-info" style="padding: 12px; margin-bottom: 8px;">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                        f'<span class="incident-id">{iid}</span>'
                        f'<div style="display:flex; gap:6px;">'
                        f'{priority_html}'
                        f'{status_html}'
                        f'</div>'
                        f'</div>'
                        f'<div class="incident-desc" style="font-size:12px; margin-top:4px;">{desc[:55]}...</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                with col_btn:
                    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
                    is_selected = st.session_state.get("selected_pred_incident_id") == iid
                    btn_label = "Active" if is_selected else "Select"
                    if st.button(btn_label, key=f"sel_pred_{iid}", use_container_width=True):
                        st.session_state["selected_pred_incident_id"] = iid
                        st.rerun()

    # ── Selected Incident Analysis (Right Side) ──
    with col_right:
        st.markdown(
            '<div class="section-title" style="margin-top:0;">Selected Incident Analysis</div>',
            unsafe_allow_html=True,
        )

        selected_id = st.session_state.get("selected_pred_incident_id")

        # Verify that the selected incident still exists in the list (or reset it)
        incident_row = None
        if selected_id and not live_df.empty:
            matches = live_df[live_df["incident_id"] == selected_id]
            if not matches.empty:
                incident_row = matches.iloc[0].to_dict()

        if not incident_row:
            st.markdown(
                '<div class="empty-state">'
                "Select an incident from the triage list to run AI analysis and routing predictions."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            # ── 1. Render Incident Details (using consistent styling) ──
            st.markdown(
                f'<div class="detail-header-id">{selected_id}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="detail-label">Description</div>'
                f'<div class="detail-value">{incident_row.get("description", "")}</div>',
                unsafe_allow_html=True,
            )

            # Metadata grid
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.markdown(
                    f'<div class="detail-label">Application</div>'
                    f'<div class="detail-value">{incident_row.get("application", "")}</div>'
                    f'<div class="detail-label">Status</div>'
                    f'<div class="detail-value">{incident_row.get("status", "")}</div>'
                    f'<div class="detail-label">Affected Users</div>'
                    f'<div class="detail-value">{int(incident_row.get("affected_users", 1))}</div>',
                    unsafe_allow_html=True,
                )
            with dcol2:
                st.markdown(
                    f'<div class="detail-label">Environment</div>'
                    f'<div class="detail-value">{incident_row.get("environment", "")}</div>'
                    f'<div class="detail-label">Priority</div>'
                    f'<div class="detail-value">{incident_row.get("priority", "")}</div>'
                    f'<div class="detail-label">Impact Scope</div>'
                    f'<div class="detail-value">{incident_row.get("impact_scope", "").replace("_", " ").title()}</div>',
                    unsafe_allow_html=True,
                )

            # Run prediction pipeline
            try:
                result = predict_incident(
                    description=incident_row["description"],
                    application=incident_row["application"],
                    affected_users=int(incident_row["affected_users"]),
                    impact_scope=incident_row["impact_scope"],
                )

                similar_incidents = get_similar_incidents(
                    description=incident_row["description"],
                    top_k=5,
                )
            except Exception as e:
                st.error(f"Triage prediction failed: {str(e)}")
                return

            vertical_spacer(24)

            # ── 2. Render ML Predictions (Cards first) ──
            st.markdown(
                '<div class="detail-section-title">ML Triage Predictions</div>',
                unsafe_allow_html=True,
            )

            p1, p2, p3 = st.columns(3)
            with p1:
                render_prediction_card("Recommended Team", result["team"])
            with p2:
                render_prediction_card("Predicted Priority", result["priority"])
            with p3:
                render_prediction_card("Est. Resolution Time", f'{round(result["resolution_time"])} min')

            vertical_spacer(24)

            # ── 3. Similar Historical Incidents (Second) ──
            st.markdown(
                '<div class="detail-section-title">Similar Historical Incidents</div>',
                unsafe_allow_html=True,
            )

            if similar_incidents:
                similar_df = pd.DataFrame(similar_incidents)[[
                    "similarity",
                    "description",
                    "team",
                    "priority",
                    "resolution_time",
                    "root_cause",
                ]]

                st.dataframe(
                    similar_df,
                    column_config={
                        "similarity": st.column_config.NumberColumn(
                            "Similarity Match",
                            format="%.2f%%",
                        ),
                        "description": st.column_config.TextColumn(
                            "Incident Description",
                            width="medium",
                        ),
                        "team": st.column_config.TextColumn("Assigned Team"),
                        "priority": st.column_config.TextColumn("Priority"),
                        "resolution_time": st.column_config.NumberColumn(
                            "Resolution Time",
                            format="%d min",
                        ),
                        "root_cause": st.column_config.TextColumn("Root Cause"),
                    },
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No similar incidents found.")

            vertical_spacer(24)

            # ── 4. Explainability (Third) ──
            st.markdown(
                '<div class="detail-section-title">AI Recommendation Rationale & Evidence</div>',
                unsafe_allow_html=True,
            )

            st.write(
                f"""
                Based on the incident description, application **{incident_row['application']}**, impact scope **{incident_row['impact_scope'].replace('_', ' ').title()}**,
                and **{int(incident_row['affected_users']):,} affected users**, the system recommends routing this incident to
                **{result['team']}** with a predicted priority of **{result['priority']}**.
                
                The estimated resolution time is **{round(result['resolution_time'])} minutes** based on historical patterns of similar incidents.
                """
            )

            vertical_spacer(16)

            if similar_incidents:
                explanation = explain_prediction(similar_incidents)

                e1, e2 = st.columns(2)
                with e1:
                    render_prediction_card(
                        "Common Team Route",
                        explanation["most_common_team"],
                        confidence=f"{explanation['team_support']}/5 matches",
                    )
                with e2:
                    render_prediction_card(
                        "Common Priority",
                        explanation["most_common_priority"],
                        confidence="Priority support",
                    )

                vertical_spacer(12)

                e3, e4 = st.columns(2)
                with e3:
                    render_prediction_card(
                        "Frequent Root Cause",
                        explanation["common_root_cause"],
                    )
                with e4:
                    render_prediction_card(
                        "Avg Resolution Time",
                        f"{explanation['avg_resolution_time']} min",
                    )
            else:
                st.info("No explainability evidence available.")