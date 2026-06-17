"""
Incident detail view component with editing/saving controls.
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

from frontend.components.cards import render_priority_badge, render_status_badge
from frontend.styles.theme import TEXT, MUTED


def _handle_status_update(incident_id: str, next_status: str) -> None:
    """Callback to handle incident status updates cleanly without visual layout shifts."""
    from backend.incident.update_incident import update_incident_status
    success, message = update_incident_status(incident_id, next_status)
    if success:
        st.toast(f"{incident_id} status updated to {next_status}.")
    else:
        st.error(message)


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
                else '<div class="timeline-step-time" style="color: transparent; user-select: none;">0000-00-00 00:00:00</div>'
            )

            st.markdown(
                f'<div class="timeline-step">'
                f'<div class="timeline-dot {dot_class}"></div>'
                f'<div class="timeline-step-content">'
                f'<div class="timeline-step-label {label_class}">{step_label}</div>'
                f'{time_html}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── SLA Status Section ──
        st.markdown(
            '<div class="detail-section-title">SLA Status</div>',
            unsafe_allow_html=True,
        )

        # We define a fragment that runs every 1.0 seconds if the incident is active (not resolved/closed/cancelled)
        is_completed = status in ("Resolved", "Closed")
        is_cancelled = status == "Cancelled"
        run_every_sec = 1.0 if not (is_completed or is_cancelled) else None

        @st.fragment(run_every=run_every_sec)
        def render_live_sla_counter() -> None:
            import json as _json
            from backend.incident.update_incident import (
                SLA_HOURS,
                _parse_pause_log,
                compute_total_paused_seconds,
                is_currently_on_hold,
                hold_incident_sla,
                resume_incident_sla,
            )

            # Re-fetch pause log each tick so it stays current after hold/resume
            from backend.incident.incident_repository import get_incident_by_id as _refetch
            _fresh = _refetch(inc_id)
            pause_log_raw = (_fresh or {}).get("sla_pause_log", "[]")
            pause_log = _parse_pause_log(pause_log_raw)

            created_at_val = incident.get("created_at")
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

            if created_at and priority in SLA_HOURS:
                hours_target = SLA_HOURS[priority]
                paused_secs = compute_total_paused_seconds(pause_log)
                sla_deadline = created_at + timedelta(hours=hours_target) + timedelta(seconds=paused_secs)
                on_hold = is_currently_on_hold(pause_log)

                def format_duration(seconds: int) -> str:
                    hours, remainder = divmod(abs(seconds), 3600)
                    minutes, secs = divmod(remainder, 60)
                    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

                if is_cancelled:
                    badge_html = '<span class="badge" style="background-color: rgba(100, 116, 139, 0.15); color: #64748B;">N/A (Cancelled)</span>'
                    st.markdown(
                        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
                        f'<div style="font-weight: 500; font-size:13px; color:#F3F4F6;">{priority} SLA: {hours_target} Hours</div>'
                        f'{badge_html}'
                        f'</div>'
                        f'<div class="detail-value">Incident was cancelled. SLA targets are not applicable.</div>',
                        unsafe_allow_html=True,
                    )
                elif not is_completed:
                    now = datetime.now()

                    if on_hold:
                        # ── SLA Paused state ──
                        badge_html = '<span class="badge" style="background-color: rgba(245, 158, 11, 0.15); color: #F59E0B;">⏸ SLA Paused</span>'
                        # Calculate how long the current pause has lasted
                        hold_start_str = pause_log[-1]["at"]
                        hold_start = datetime.strptime(hold_start_str, "%Y-%m-%d %H:%M:%S")
                        paused_for = int((now - hold_start).total_seconds())

                        st.markdown(
                            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
                            f'<div style="font-weight: 500; font-size:13px; color:#F3F4F6;">{priority} SLA: {hours_target} Hours</div>'
                            f'{badge_html}'
                            f'</div>'
                            f'<div class="detail-label" style="margin-bottom:2px;">Deadline (adjusted)</div>'
                            f'<div class="detail-value" style="font-family: \'SF Mono\', monospace; font-size: 13px; margin-bottom:12px;">{sla_deadline.strftime("%Y-%m-%d %H:%M:%S")}</div>'
                            f'<div class="detail-label" style="margin-bottom:2px;">Paused For</div>'
                            f'<div class="detail-value" style="font-family: \'SF Mono\', monospace; font-size: 16px; font-weight: 600; color: #F59E0B;">{format_duration(paused_for)}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        # ── SLA Running state ──
                        time_diff = (sla_deadline - now).total_seconds()

                        if time_diff > 0:
                            color_type = "orange" if time_diff < 1800 else "green"
                            status_label = "On Track"
                            badge_html = f'<span class="badge" style="background-color: {"rgba(245, 158, 11, 0.15)" if color_type == "orange" else "rgba(16, 185, 129, 0.15)"}; color: {"#F59E0B" if color_type == "orange" else "#10B981"};">{status_label}</span>'
                            time_label = "Time Remaining"
                            time_value = format_duration(int(time_diff))
                        else:
                            badge_html = '<span class="badge" style="background-color: rgba(239, 68, 68, 0.15); color: #EF4444;">SLA Breached</span>'
                            time_label = "Exceeded By"
                            time_value = format_duration(int(time_diff))

                        deadline_label = "Deadline (adjusted)" if paused_secs > 0 else "Deadline"
                        time_color = "#F59E0B" if (time_diff > 0 and time_diff < 1800) else ("#10B981" if time_diff > 0 else "#EF4444")

                        st.markdown(
                            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
                            f'<div style="font-weight: 500; font-size:13px; color:#F3F4F6;">{priority} SLA: {hours_target} Hours</div>'
                            f'{badge_html}'
                            f'</div>'
                            f'<div class="detail-label" style="margin-bottom:2px;">{deadline_label}</div>'
                            f'<div class="detail-value" style="font-family: \'SF Mono\', monospace; font-size: 13px; margin-bottom:12px;">{sla_deadline.strftime("%Y-%m-%d %H:%M:%S")}</div>'
                            f'<div class="detail-label" style="margin-bottom:2px;">{time_label}</div>'
                            f'<div class="detail-value" style="font-family: \'SF Mono\', monospace; font-size: 16px; font-weight: 600; color: {time_color};">{time_value}</div>',
                            unsafe_allow_html=True,
                        )

                    # ── Hold / Resume toggle (only when In Progress) ──
                    if status == "In Progress":
                        st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
                        if on_hold:
                            if st.button("▶ Resume SLA", key=f"sla_resume_{inc_id}", use_container_width=True):
                                ok, msg = resume_incident_sla(inc_id)
                                if ok:
                                    st.toast("SLA clock resumed.")
                                else:
                                    st.error(msg)
                                st.rerun()
                        else:
                            if st.button("⏸ Hold SLA", key=f"sla_hold_{inc_id}", use_container_width=True):
                                ok, msg = hold_incident_sla(inc_id)
                                if ok:
                                    st.toast("SLA clock paused — forwarded to third party.")
                                else:
                                    st.error(msg)
                                st.rerun()
                else:
                    # ── Completed incident — show final SLA result ──
                    comp_val = incident.get("closed_at") if incident.get("closed_at") else incident.get("resolved_at")
                    completion_time = None
                    if comp_val:
                        if isinstance(comp_val, str):
                            try:
                                completion_time = datetime.strptime(comp_val, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                completion_time = pd.to_datetime(comp_val).to_pydatetime()
                        else:
                            if hasattr(comp_val, "to_pydatetime"):
                                completion_time = comp_val.to_pydatetime()
                            else:
                                completion_time = comp_val

                    is_breached = incident.get("sla_breached") == True
                    if completion_time:
                        is_breached = completion_time > sla_deadline

                    if not is_breached:
                        badge_html = '<span class="badge" style="background-color: rgba(16, 185, 129, 0.15); color: #10B981;">Met SLA</span>'
                        time_label = "Completed Early By"
                        time_diff = (sla_deadline - (completion_time or datetime.now())).total_seconds() if completion_time else 0
                        time_value = format_duration(int(time_diff))
                    else:
                        badge_html = '<span class="badge" style="background-color: rgba(239, 68, 68, 0.15); color: #EF4444;">Breached SLA</span>'
                        time_label = "Exceeded By"
                        time_diff = ((completion_time or datetime.now()) - sla_deadline).total_seconds() if completion_time else 0
                        time_value = format_duration(int(time_diff))

                    deadline_label = "Deadline (adjusted)" if paused_secs > 0 else "Deadline"

                    st.markdown(
                        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">'
                        f'<div style="font-weight: 500; font-size:13px; color:#F3F4F6;">{priority} SLA: {hours_target} Hours</div>'
                        f'{badge_html}'
                        f'</div>'
                        f'<div class="detail-label" style="margin-bottom:2px;">{deadline_label}</div>'
                        f'<div class="detail-value" style="font-family: \'SF Mono\', monospace; font-size: 13px; margin-bottom:12px;">{sla_deadline.strftime("%Y-%m-%d %H:%M:%S")}</div>'
                        f'<div class="detail-label" style="margin-bottom:2px;">{time_label}</div>'
                        f'<div class="detail-value" style="font-family: \'SF Mono\', monospace; font-size: 16px; font-weight: 600; color: {"#10B981" if not is_breached else "#EF4444"};">{time_value}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("SLA Status could not be calculated (Created timestamp or Priority is missing).")

        render_live_sla_counter()

        # ── L3 Escalation Advisor Section ──
        st.markdown(
            '<div class="detail-section-title">L3 Escalation Advisor</div>',
            unsafe_allow_html=True,
        )

        # Check if L3 escalation analysis has already been generated
        risk_val = incident.get("l3_escalation_risk")
        reasons_val = incident.get("l3_escalation_reasons")
        rec_team_val = incident.get("l3_escalation_team")
        escalate_val = incident.get("l3_escalation_recommended")

        import json as _json
        has_l3_data = (
            risk_val is not None 
            and not pd.isna(risk_val)
            and reasons_val is not None
            and str(reasons_val).strip() != ""
        )

        if not has_l3_data:
            # We must run it dynamically!
            try:
                # 1. Get similar incidents
                from backend.ml.similar_incidents import get_similar_incidents as _get_sim
                similar_incidents = _get_sim(description=incident.get("description", ""), top_k=5)
            except Exception:
                similar_incidents = []

            try:
                # 2. Get root cause analysis
                from backend.ml.root_cause_agent import analyze_root_cause as _arc
                temp_incident_dict = {
                    "incident_id": inc_id,
                    "description": incident.get("description"),
                    "application": incident.get("application"),
                    "category": incident.get("category"),
                    "impact_scope": incident.get("impact_scope"),
                    "affected_users": incident.get("affected_users")
                }
                rc_analysis = _arc(temp_incident_dict, similar_incidents)
            except Exception as e:
                rc_analysis = {
                    "root_cause": "Pending Analysis",
                    "confidence": 50,
                    "investigation_steps": [],
                    "explanation": f"Unable to fetch generative analysis: {str(e)}"
                }

            # 3. Compute SLA details (sla_breached, sla_remaining_minutes)
            created_at_val = incident.get("created_at")
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

            # Use update_incident SLA hours limit
            from backend.incident.update_incident import SLA_HOURS, _parse_pause_log, compute_total_paused_seconds
            
            prio = incident.get("priority")
            sla_breached_calc = False
            sla_rem_mins_calc = 0
            if created_at and prio in SLA_HOURS:
                hours_target = SLA_HOURS[prio]
                pause_log_raw = incident.get("sla_pause_log", "[]")
                pause_log = _parse_pause_log(pause_log_raw)
                paused_secs = compute_total_paused_seconds(pause_log)
                sla_deadline = created_at + timedelta(hours=hours_target) + timedelta(seconds=paused_secs)
                
                is_completed = status in ("Resolved", "Closed")
                if is_completed:
                    comp_val = incident.get("closed_at") or incident.get("resolved_at")
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

                sla_breached_calc = time_diff < 0
                try:
                    sla_rem_mins_calc = int(time_diff)
                except (ValueError, TypeError):
                    sla_rem_mins_calc = 0

            try:
                # 4. Invoke Advisor
                from backend.ml.l3_escalation_advisor import analyze_l3_escalation as _ale
                from backend.ml.predict_incident import predict_incident as _pi
                
                pred_team = incident.get("ai_predicted_team") or incident.get("predicted_team")
                pred_priority = incident.get("ai_predicted_priority") or incident.get("predicted_priority")
                pred_res_time = incident.get("ai_predicted_resolution_time") or incident.get("predicted_resolution_time")

                if not pred_team:
                    try:
                        pred_res = _pi(
                            description=incident.get("description", ""),
                            application=incident.get("application", ""),
                            affected_users=int(incident.get("affected_users", 0)),
                            impact_scope=incident.get("impact_scope", "")
                        )
                        pred_team = pred_res.get("team")
                        pred_priority = pred_res.get("priority")
                        pred_res_time = pred_res.get("resolution_time")
                    except Exception:
                        pred_team = incident.get("teams", "")
                        pred_priority = prio
                        pred_res_time = 0.0

                l3_incident_input = {
                    "description": incident.get("description"),
                    "application": incident.get("application"),
                    "affected_users": incident.get("affected_users"),
                    "impact_scope": incident.get("impact_scope"),
                    "priority": prio,
                    "predicted_team": pred_team,
                    "predicted_priority": pred_priority,
                    "predicted_resolution_time": pred_res_time,
                    "sla_risk": {
                        "sla_breached": sla_breached_calc,
                        "sla_remaining_minutes": sla_rem_mins_calc
                    }
                }

                l3_analysis = _ale(l3_incident_input, similar_incidents, rc_analysis)
            except Exception as e:
                l3_analysis = {
                    "risk_score": 0,
                    "escalate": False,
                    "recommended_team": incident.get("teams", "L2 Support"),
                    "reasons": [f"Error running advisor dynamically: {str(e)}"]
                }

            risk_val = l3_analysis["risk_score"]
            escalate_val = l3_analysis["escalate"]
            rec_team_val = l3_analysis["recommended_team"]
            reasons_list = l3_analysis["reasons"]
            reasons_val = _json.dumps(reasons_list)

            # Persist to SQLite
            from backend.database.incident_repository import update_l3_escalation as _ule
            _ule(
                incident_id=inc_id,
                risk=risk_val,
                recommended=escalate_val,
                team=rec_team_val,
                reasons=reasons_list
            )
        else:
            # Parse reasons from DB JSON text
            try:
                reasons_list = _json.loads(reasons_val)
            except Exception:
                reasons_list = [str(reasons_val)]
            risk_val = int(risk_val)
            escalate_val = bool(escalate_val)
            rec_team_val = str(rec_team_val)

        # ── Display Advisor metrics on UI ──
        if risk_val <= 30:
            risk_band = "Low Risk"
            risk_color = "#10B981"  # Green
        elif risk_val <= 60:
            risk_band = "Medium Risk"
            risk_color = "#F59E0B"  # Orange
        elif risk_val <= 80:
            risk_band = "High Risk"
            risk_color = "#F97316"  # Dark Orange / Orange-Red
        else:
            risk_band = "Critical Risk"
            risk_color = "#EF4444"  # Red

        col_risk, col_rec = st.columns([0.4, 0.6])
        with col_risk:
            st.markdown(
                f"""
                <div class="prediction-card" style="border-top: 4px solid {risk_color}; padding: 12px; min-height: 100px;">
                    <div class="pred-label" style="font-size: 11px; margin-bottom: 4px;">Risk Score</div>
                    <div class="pred-value" style="color: {risk_color}; font-size: 22px; font-weight: 700;">{risk_val}%</div>
                    <div class="pred-confidence" style="color: {risk_color}; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-top: 2px;">{risk_band}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_rec:
            if escalate_val:
                # Clean team name
                cleaned_team = rec_team_val.strip()
                if cleaned_team.upper().startswith("L3"):
                    cleaned_team = cleaned_team[2:].strip()
                if cleaned_team.lower().endswith("team"):
                    cleaned_team = cleaned_team[:-4].strip()
                rec_text = f"Escalate to L3 {cleaned_team} Team"
                rec_color = "#EF4444"
            else:
                rec_text = "Continue with L2 Support"
                rec_color = "#10B981"

            st.markdown(
                f"""
                <div style="padding: 12px; background-color: #0F121E; border: 1px solid #1B223C; border-radius: 12px; min-height: 100px; display: flex; flex-direction: column; justify-content: center; text-align: center;">
                    <div class="detail-label" style="font-size: 11px; margin-bottom: 4px;">Recommendation</div>
                    <div style="font-size: 13px; font-weight: 600; color: {rec_color}; line-height: 1.4;">{rec_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        for r in reasons_list:
            st.markdown(
                f'<div style="margin-left: 12px; margin-bottom: 4px; font-size: 12px; color: #b1b2b3;">'
                f'&bull; {r}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

        # ── Status Update Actions (only visible when not editing) ──
        from backend.incident.update_incident import get_valid_transitions

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
                    st.button(
                        button_label,
                        key=f"update_btn_{inc_id}_{next_status}",
                        use_container_width=True,
                        on_click=_handle_status_update,
                        args=(inc_id, next_status),
                    )
        else:
            st.markdown(
                f'<div style="margin-top:16px; color:{MUTED}; font-size:13px;">'
                f"This incident is in a terminal state ({status})."
                f"</div>",
                unsafe_allow_html=True,
            )

