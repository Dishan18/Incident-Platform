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


@st.dialog("Create New Incident", width="large", dismissible=False)
def _new_incident_dialog() -> None:
    """Modal dialog for creating a new incident."""

    # ── Step A: Check if a submission is pending (set by Submit button callback) ──
    if st.session_state.get("dup_submit_pending", False):
        desc_val = st.session_state.get("new_inc_desc", "").strip()
        if desc_val:
            from backend.ml.similar_incidents import get_similar_incidents

            matches = get_similar_incidents(desc_val, top_k=5, active_only=True)
            dup_matches = [m for m in matches if m["similarity"] >= 80.0]
            if dup_matches:
                # Store matches and stay in this dialog run to show warning
                st.session_state["dup_check_matches"] = dup_matches
                st.session_state["dup_submit_pending"] = False  # consumed
            else:
                # No duplicates — create immediately
                incident = create_incident(
                    description=desc_val,
                    application=st.session_state.get("new_inc_app"),
                    affected_users=int(st.session_state.get("new_inc_users", 1)),
                    impact_scope=st.session_state.get("new_inc_scope", "single_user"),
                    environment=st.session_state.get("new_inc_env", "Production"),
                )
                st.toast(f"Incident {incident['incident_id']} created.")
                _close_dialog()
                return
        else:
            st.session_state["dup_submit_pending"] = False

    # ── Step B: Show duplicate warning if matches exist ──
    if "dup_check_matches" in st.session_state:
        matches = st.session_state["dup_check_matches"]
        st.warning("⚠️ Similar Active Incident Found")
        st.markdown(
            "The incident description you entered is highly similar to one or more active incidents "
            "currently being worked on. Please review the details below before choosing how to proceed:"
        )

        top_match = matches[0]
        sim_val = top_match["similarity"]

        if sim_val >= 90.0:
            classification = "Probable Duplicate"
            badge_color = "#EF4444"
        else:
            classification = "Related Incident"
            badge_color = "#F59E0B"

        st.markdown(
            f"""
            <div style="background-color: #0F121E; border: 1px solid #1B223C; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-weight: 700; font-size: 1.1em; color: #F3F4F6;">{top_match['incident_id']}</span>
                    <span style="background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">{classification} ({sim_val}%)</span>
                </div>
                <div style="font-size: 0.95em; color: #F3F4F6; margin-bottom: 10px;"><strong>Description:</strong> {top_match['description']}</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em; color: #94A3B8;">
                    <div><strong>Status:</strong> {top_match['status']}</div>
                    <div><strong>Assigned Team:</strong> {top_match['team']}</div>
                    <div><strong>Application:</strong> {top_match.get('application', 'N/A')}</div>
                    <div><strong>Created:</strong> {top_match['created_at']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        vertical_spacer(10)

        col_view, col_anyway, col_back = st.columns(3)
        with col_view:
            if st.button("View Incident", use_container_width=True):
                st.session_state["selected_incident_id"] = top_match["incident_id"]
                _close_dialog()

        with col_anyway:
            if st.button("Create Anyway", use_container_width=True):
                incident = create_incident(
                    description=st.session_state.get("new_inc_desc", ""),
                    application=st.session_state.get("new_inc_app"),
                    affected_users=int(st.session_state.get("new_inc_users", 1)),
                    impact_scope=st.session_state.get("new_inc_scope", "single_user"),
                    environment=st.session_state.get("new_inc_env", "Production"),
                )
                st.toast(f"Incident {incident['incident_id']} created.")
                _close_dialog()

        with col_back:
            if st.button("Go Back & Edit", use_container_width=True):
                if "dup_check_matches" in st.session_state:
                    del st.session_state["dup_check_matches"]
                st.rerun()
        return

    # ── Step C: Render the standard input form ──
    st.text_area(
        "Description",
        placeholder="Describe the incident symptoms and impact...",
        height=100,
        key="new_inc_desc",
    )

    applications = sorted(APP_TEAM_MAP.keys())
    st.selectbox("Application", applications, key="new_inc_app")

    col_a, col_b = st.columns(2)
    with col_a:
        st.number_input("Affected Users", min_value=1, value=1, step=1, key="new_inc_users")
    with col_b:
        scopes = ["single_user", "department", "site", "enterprise"]
        st.selectbox("Impact Scope", scopes, key="new_inc_scope")

    envs = ["Production", "UAT", "Development"]
    st.selectbox("Environment", envs, key="new_inc_env")

    vertical_spacer(12)

    col_submit, col_cancel = st.columns(2)
    with col_submit:
        st.button(
            "Submit Incident",
            use_container_width=True,
            on_click=_on_submit_incident,
        )
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            _close_dialog()


def _on_submit_incident() -> None:
    """Button callback — sets a flag so the next dialog rerun performs the dup check."""
    st.session_state["dup_submit_pending"] = True


def _close_dialog() -> None:
    """Clean up all dialog-related session state and close the dialog."""
    st.session_state["show_new_incident_dialog"] = False
    for k in [
        "new_inc_desc", "new_inc_app", "new_inc_users", "new_inc_scope",
        "new_inc_env", "dup_check_matches", "dup_submit_pending",
    ]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


@st.dialog("Root Cause Analysis (RCA) Questionnaire", width="medium", dismissible=True)
def _rca_dialog(incident: dict) -> None:
    st.markdown(
        f"Generate a Root Cause Analysis report for incident **{incident['incident_id']}**."
    )

    actual_rc = st.text_area(
        "What was the actual root cause identified? *",
        placeholder="e.g. Expired VPN certificate",
        key="rca_q_actual_rc"
    )

    resolution_action = st.text_area(
        "What action resolved the incident? *",
        placeholder="e.g. Certificate renewed and tunnel re-established",
        key="rca_q_resolution"
    )

    preventive_measure = st.text_area(
        "What preventive measure should be implemented to avoid recurrence? *",
        placeholder="e.g. Enable certificate expiry monitoring",
        key="rca_q_preventive"
    )

    additional_notes = st.text_area(
        "Additional notes (optional)",
        placeholder="Provide any other relevant context...",
        key="rca_q_notes"
    )

    col_submit, col_cancel = st.columns(2)
    with col_submit:
        if st.button("Generate RCA", use_container_width=True, key="rca_q_submit_btn"):
            if not actual_rc.strip() or not resolution_action.strip() or not preventive_measure.strip():
                st.error("Please fill in all mandatory fields (*).")
            else:
                with st.spinner("Generating RCA using AI..."):
                    from backend.incident.generate_rca import generate_rca
                    try:
                        generate_rca(
                            incident_id=incident["incident_id"],
                            actual_root_cause=actual_rc.strip(),
                            resolution_action=resolution_action.strip(),
                            preventive_measure=preventive_measure.strip(),
                            additional_notes=additional_notes.strip()
                        )
                        st.toast("RCA generated successfully.")
                        _close_rca_dialog()
                    except Exception as e:
                        st.error(f"Error generating RCA: {e}")

    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="rca_q_cancel_btn"):
            _close_rca_dialog()


def _close_rca_dialog() -> None:
    st.session_state["show_rca_dialog"] = False
    for k in ["rca_q_actual_rc", "rca_q_resolution", "rca_q_preventive", "rca_q_notes"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


@st.dialog("Edit RCA", width="medium", dismissible=True)
def _edit_rca_dialog(incident: dict) -> None:
    st.markdown(
        f"Manually edit the Root Cause Analysis report for incident **{incident['incident_id']}**."
    )

    rca_content = incident.get("rca_content")
    import json
    rca_data = {}
    if rca_content:
        try:
            if isinstance(rca_content, str):
                rca_data = json.loads(rca_content)
            elif isinstance(rca_content, dict):
                rca_data = rca_content
        except Exception:
            pass

    summary_val = st.text_area(
        "Summary",
        value=rca_data.get("summary", ""),
        key="edit_rca_summary"
    )
    root_cause_val = st.text_area(
        "Root Cause",
        value=rca_data.get("root_cause", ""),
        key="edit_rca_root_cause"
    )
    resolution_val = st.text_area(
        "Resolution",
        value=rca_data.get("resolution", ""),
        key="edit_rca_resolution"
    )
    preventive_val = st.text_area(
        "Preventive Action",
        value=rca_data.get("preventive_action", ""),
        key="edit_rca_preventive"
    )

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save Changes", use_container_width=True, key="edit_rca_save_btn"):
            edited_rca = {
                "summary": summary_val.strip(),
                "root_cause": root_cause_val.strip(),
                "resolution": resolution_val.strip(),
                "preventive_action": preventive_val.strip()
            }
            from backend.database.incident_repository import update_rca, get_incident
            from datetime import datetime

            edited_rca_str = json.dumps(edited_rca)
            success = update_rca(
                incident_id=incident["incident_id"],
                rca_content=edited_rca_str,
                rca_generated_at=datetime.now()
            )
            if success:
                try:
                    updated_inc = get_incident(incident["incident_id"])
                    if updated_inc:
                        updated_dict = {
                            "incident_id": updated_inc.incident_id,
                            "description": updated_inc.description,
                            "application": updated_inc.application,
                            "category": updated_inc.category,
                            "priority": updated_inc.priority,
                            "status": updated_inc.status,
                            "rca_generated_at": updated_inc.rca_generated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_inc.rca_generated_at else "",
                            "rca_content": updated_inc.rca_content
                        }

                        from backend.incident.generate_rca import build_rca_pdf
                        from backend.cloud.azure_blob import upload_file
                        from datetime import date

                        pdf_bytes = build_rca_pdf(updated_dict)
                        filename = f"{updated_inc.incident_id}-RCA-{date.today()}.pdf"
                        blob_url = upload_file(pdf_bytes, filename, container_name="rca-files")

                        # Store the updated PDF URL
                        update_rca(
                            incident_id=updated_inc.incident_id,
                            rca_content=updated_inc.rca_content,
                            rca_generated_at=updated_inc.rca_generated_at,
                            rca_pdf_url=blob_url
                        )
                except Exception as upload_err:
                    print(f"Error rebuilding/uploading PDF on edit: {upload_err}")

                st.toast("RCA updated successfully.")
                _close_edit_rca_dialog()
            else:
                st.error("Failed to save changes to the database.")

    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="edit_rca_cancel_btn"):
            _close_edit_rca_dialog()


def _close_edit_rca_dialog() -> None:
    st.session_state["show_edit_rca_dialog"] = False
    for k in ["edit_rca_summary", "edit_rca_root_cause", "edit_rca_resolution", "edit_rca_preventive"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


@st.dialog("Regenerate RCA", width="medium", dismissible=True)
def _regenerate_rca_dialog(incident: dict) -> None:
    st.warning("⚠️ Existing RCA will be replaced.")
    st.markdown(
        "This action will generate a completely new RCA using the incident details and questionnaire responses."
    )

    col_confirm, col_cancel = st.columns(2)
    with col_confirm:
        if st.button("Generate New RCA", use_container_width=True, key="regen_rca_confirm_btn"):
            st.session_state["show_regen_rca_dialog"] = False
            st.session_state["show_rca_dialog"] = True
            st.rerun()

    with col_cancel:
        if st.button("Cancel", use_container_width=True, key="regen_rca_cancel_btn"):
            st.session_state["show_regen_rca_dialog"] = False
            st.rerun()


def render_incidents() -> None:
    """Render the Incidents management page."""
    if "show_new_incident_dialog" not in st.session_state:
        st.session_state["show_new_incident_dialog"] = False

    selected_id = st.session_state.get("selected_incident_id")

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
            st.session_state["show_new_incident_dialog"] = True
            # Clean any stale state from previous dialog sessions
            for k in [
                "dup_check_matches", "dup_submit_pending",
                "new_inc_desc", "new_inc_app", "new_inc_users",
                "new_inc_scope", "new_inc_env",
            ]:
                if k in st.session_state:
                    del st.session_state[k]

    if st.session_state.get("show_new_incident_dialog", False):
        _new_incident_dialog()

    if st.session_state.get("show_rca_dialog", False) and selected_id:
        incident = get_incident_by_id(selected_id)
        if incident:
            _rca_dialog(incident)

    if st.session_state.get("show_edit_rca_dialog", False) and selected_id:
        incident = get_incident_by_id(selected_id)
        if incident:
            _edit_rca_dialog(incident)

    if st.session_state.get("show_regen_rca_dialog", False) and selected_id:
        incident = get_incident_by_id(selected_id)
        if incident:
            _regenerate_rca_dialog(incident)

    # Consistent border-bottom separator matching the page header container
    st.markdown('<hr style="margin-top:0px; margin-bottom:16px;">', unsafe_allow_html=True)

    # ── Filters Bar ──
    live_df = get_live_incidents()
    today_date = datetime.now().date()

    with st.container():
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)

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
            preferred_order = ["Unix/Linux", "Wintel", "Batch", "Middleware", "Network", "Database"]
            all_teams: set[str] = set()
            if not live_df.empty:
                for teams_str in live_df["teams"].dropna():
                    for t in str(teams_str).split(","):
                        if t.strip():
                            all_teams.add(t.strip())
            all_teams = all_teams.union(preferred_order)
            teams_list = [t for t in preferred_order if t in all_teams] + sorted(list(all_teams - set(preferred_order)))
            selected_teams = st.multiselect("Teams", teams_list, key="inc_filter_teams")

        with col_f5:
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

        if selected_teams:
            def matches_any_team(teams_str):
                if pd.isna(teams_str) or not str(teams_str).strip():
                    return False
                incident_teams = {t.strip() for t in str(teams_str).split(",") if t.strip()}
                return not incident_teams.isdisjoint(selected_teams)
            filtered_df = filtered_df[filtered_df["teams"].apply(matches_any_team)]

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
