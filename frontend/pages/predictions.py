"""
Predictions page -- Incident Intelligence Center.
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

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

        preferred_order = ["Unix/Linux", "Wintel", "Batch", "Middleware", "Network", "Database"]
        all_teams: set[str] = set()
        if not live_df.empty:
            for teams_str in live_df["teams"].dropna():
                for t in str(teams_str).split(","):
                    if t.strip():
                        all_teams.add(t.strip())
        all_teams = all_teams.union(preferred_order)
        teams_list = [t for t in preferred_order if t in all_teams] + sorted(list(all_teams - set(preferred_order)))
        selected_teams = st.multiselect("Teams", teams_list, key="pred_filter_teams")

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

            if selected_teams:
                def matches_any_team(teams_str):
                    if pd.isna(teams_str) or not str(teams_str).strip():
                        return False
                    incident_teams = {t.strip() for t in str(teams_str).split(",") if t.strip()}
                    return not incident_teams.isdisjoint(selected_teams)
                filtered_live = filtered_live[filtered_live["teams"].apply(matches_any_team)]

            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                filtered_live = filtered_live[
                    (filtered_live["created_at_dt"].dt.date >= start_date) &
                    (filtered_live["created_at_dt"].dt.date <= end_date)
                ]
            
            if not filtered_live.empty:
                filtered_live = filtered_live.sort_values(["created_at", "incident_id"], ascending=[False, False])

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

            # Call Root Cause Agent (cached in session state per selected incident, only if successful)
            rc_cache_key = f"rc_analysis_{selected_id}"
            is_fallback = False
            if rc_cache_key in st.session_state:
                rc_analysis = st.session_state[rc_cache_key]
                if rc_analysis.get("explanation", "").startswith("Unable to fetch generative analysis"):
                    is_fallback = True
            
            if rc_cache_key not in st.session_state or is_fallback:
                with st.spinner("Running Gemini Root Cause Agent Analysis..."):
                    from backend.ml.root_cause_agent import analyze_root_cause
                    rc_analysis = analyze_root_cause(incident_row, similar_incidents)
                    # If it's a valid analysis (not the fallback/failed one), cache it
                    if not rc_analysis.get("explanation", "").startswith("Unable to fetch generative analysis"):
                        st.session_state[rc_cache_key] = rc_analysis

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

            # ── Gemini Root Cause Analysis ──
            vertical_spacer(24)
            col_sec_title, col_sec_btn = st.columns([0.75, 0.25])
            with col_sec_title:
                st.markdown(
                    '<div class="detail-section-title" style="margin-top:0;">AI Agent Root Cause Analysis</div>',
                    unsafe_allow_html=True,
                )
            with col_sec_btn:
                if st.button("Re-analyze", key=f"re_analyze_{selected_id}", use_container_width=True):
                    if rc_cache_key in st.session_state:
                        del st.session_state[rc_cache_key]
                    l3_cache_key = f"l3_analysis_{selected_id}"
                    if l3_cache_key in st.session_state:
                        del st.session_state[l3_cache_key]
                    st.rerun()

            col_rc, col_conf = st.columns([0.7, 0.3])
            with col_rc:
                st.markdown(
                    f'<div class="detail-label">Predicted Root Cause</div>'
                    f'<div class="detail-value prediction-highlight">'
                    f'{rc_analysis.get("root_cause", "Pending Analysis")}</div>',
                    unsafe_allow_html=True,
                )
            with col_conf:
                st.markdown(
                    f'<div class="detail-label">Confidence Score</div>'
                    f'<div class="detail-value prediction-highlight">'
                    f'{rc_analysis.get("confidence", 0)}%</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div class="detail-label">Incident Explanation</div>'
                f'<div class="detail-value" style="font-style: italic; font-size: 13px;">'
                f'{rc_analysis.get("explanation", "")}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="detail-label">Recommended Investigation Steps</div>',
                unsafe_allow_html=True,
            )
            for step in rc_analysis.get("investigation_steps", []):
                st.markdown(
                    f'<div class="reason-bullet-item">&bull; {step}</div>',
                    unsafe_allow_html=True,
                )

            # Calculate SLA status for the prompt
            from backend.incident.update_incident import SLA_HOURS, _parse_pause_log, compute_total_paused_seconds
            created_at_val = incident_row.get("created_at")
            created_at = None
            if created_at_val:
                if isinstance(created_at_val, str):
                    try:
                        created_at = datetime.strptime(created_at_val, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        created_at = pd.to_datetime(created_at_val).to_pydatetime()
                else:
                    if hasattr(created_at_val, "to_pydatetime"):
                        created_at = created_at_val.to_pydatetime()
                    else:
                        created_at = created_at_val

            priority = incident_row.get("priority")
            sla_breached = False
            sla_remaining_minutes = 0
            if created_at and priority in SLA_HOURS:
                hours_target = SLA_HOURS[priority]
                pause_log_raw = incident_row.get("sla_pause_log", "[]")
                pause_log = _parse_pause_log(pause_log_raw)
                paused_secs = compute_total_paused_seconds(pause_log)
                sla_deadline = created_at + timedelta(hours=hours_target) + timedelta(seconds=paused_secs)
                
                status = incident_row.get("status", "")
                is_completed = status in ("Resolved", "Closed")
                if is_completed:
                    comp_val = incident_row.get("closed_at") or incident_row.get("resolved_at")
                    comp_time = None
                    if comp_val and not pd.isna(comp_val) and str(comp_val).strip() not in ("", "nan", "NaT", "None"):
                        if isinstance(comp_val, str):
                            try:
                                comp_time = datetime.strptime(comp_val, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                try:
                                    comp_time = pd.to_datetime(comp_val).to_pydatetime()
                                except Exception:
                                    comp_time = None
                        else:
                            if hasattr(comp_val, "to_pydatetime"):
                                try:
                                    comp_time = comp_val.to_pydatetime()
                                except Exception:
                                    comp_time = None
                            else:
                                comp_time = comp_val
                    
                    if comp_time is None or pd.isna(comp_time):
                        comp_time = None

                    time_diff = (sla_deadline - (comp_time or datetime.now())).total_seconds() / 60
                else:
                    time_diff = (sla_deadline - datetime.now()).total_seconds() / 60
                
                if pd.isna(time_diff):
                    time_diff = 0.0

                sla_breached = time_diff < 0
                try:
                    sla_remaining_minutes = int(time_diff)
                except (ValueError, TypeError):
                    sla_remaining_minutes = 0

            # L3 escalation analysis cached call
            l3_cache_key = f"l3_analysis_{selected_id}"
            is_l3_fallback = False
            if l3_cache_key in st.session_state:
                l3_analysis = st.session_state[l3_cache_key]
                if l3_analysis.get("reasons") == ["Error running escalation advisor"]:
                    is_l3_fallback = True

            if l3_cache_key not in st.session_state or is_l3_fallback:
                with st.spinner("Running L3 Escalation Analysis..."):
                    from backend.ml.l3_escalation_advisor import analyze_l3_escalation
                    # Build incident dict to pass to Gemini
                    l3_incident_input = incident_row.copy()
                    l3_incident_input["sla_risk"] = {
                        "sla_breached": sla_breached,
                        "sla_remaining_minutes": sla_remaining_minutes
                    }
                    l3_incident_input["predicted_team"] = result["team"]
                    l3_incident_input["predicted_priority"] = result["priority"]
                    l3_incident_input["predicted_resolution_time"] = result["resolution_time"]
                    
                    l3_analysis = analyze_l3_escalation(
                        incident=l3_incident_input,
                        similar_incidents=similar_incidents,
                        root_cause_analysis=rc_analysis
                    )
                    st.session_state[l3_cache_key] = l3_analysis
                    
                    # Persist results to database
                    from backend.database.incident_repository import update_l3_escalation
                    update_l3_escalation(
                        incident_id=selected_id,
                        risk=l3_analysis["risk_score"],
                        recommended=l3_analysis["escalate"],
                        team=l3_analysis["recommended_team"],
                        reasons=l3_analysis["reasons"]
                    )

            # ── L3 Escalation Advisor Section ──
            vertical_spacer(24)
            st.markdown(
                '<div class="detail-section-title">L3 Escalation Advisor</div>',
                unsafe_allow_html=True,
            )

            # Risk bands configuration
            risk_score = l3_analysis.get("risk_score", 0)
            if risk_score <= 30:
                risk_band = "Low Risk"
                risk_color = "#10B981"  # Green
            elif risk_score <= 60:
                risk_band = "Medium Risk"
                risk_color = "#F59E0B"  # Orange
            elif risk_score <= 80:
                risk_band = "High Risk"
                risk_color = "#F97316"  # Dark Orange / Orange-Red
            else:
                risk_band = "Critical Risk"
                risk_color = "#EF4444"  # Red

            col_risk, col_rec = st.columns([0.4, 0.6])
            with col_risk:
                st.markdown(
                    f"""
                    <div class="prediction-card" style="border-top: 4px solid {risk_color}; height: 100%;">
                        <div class="pred-label">Risk Score</div>
                        <div class="pred-value" style="color: {risk_color}; font-size: 32px; font-weight: 700;">{risk_score}%</div>
                        <div class="pred-confidence" style="color: {risk_color}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px;">{risk_band}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_rec:
                escalate = l3_analysis.get("escalate", False)
                recommended_team = l3_analysis.get("recommended_team", "")
                if escalate:
                    # Clean team name
                    cleaned_team = recommended_team.strip()
                    if cleaned_team.upper().startswith("L3"):
                        cleaned_team = cleaned_team[2:].strip()
                    if cleaned_team.lower().endswith("team"):
                        cleaned_team = cleaned_team[:-4].strip()
                    rec_val = f"Escalate to L3 {cleaned_team} Team"
                    rec_color = "#EF4444"
                else:
                    rec_val = "Continue with L2 Support"
                    rec_color = "#10B981"

                st.markdown(
                    f"""
                    <div class="escalation-rec-box">
                        <div class="detail-label" style="margin-bottom: 8px;">Escalation Recommendation</div>
                        <div style="font-size: 16px; font-weight: 600; color: {rec_color}; line-height: 1.4;">{rec_val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div class="detail-label" style="margin-top: 16px; margin-bottom: 8px;">Reasons</div>',
                unsafe_allow_html=True,
            )
            reasons_list = l3_analysis.get("reasons", [])
            for r in reasons_list:
                st.markdown(
                    f'<div class="reason-bullet-item">&bull; {r}</div>',
                    unsafe_allow_html=True,
                )

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