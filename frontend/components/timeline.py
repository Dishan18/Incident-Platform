"""
Timeline view component for the Incidents page.
Renders incidents grouped by date as styled cards with selection buttons.
"""

import streamlit as st

from frontend.components.cards import render_priority_badge, render_status_badge


def render_timeline(incidents_by_date: dict) -> None:
    """Render incidents grouped by date in a timeline layout.

    Each incident card includes a *View* button that sets
    ``st.session_state["selected_incident_id"]`` on click.

    Parameters
    ----------
    incidents_by_date : dict
        Mapping of date labels to lists of incident dicts,
        as returned by ``get_incidents_grouped_by_date()``.
    """
    if not incidents_by_date:
        st.markdown(
            '<div class="empty-state">'
            "No incidents found. Create a new incident to get started."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    for date_label, incidents in incidents_by_date.items():
        st.markdown(
            f'<div class="date-header">{date_label}</div>',
            unsafe_allow_html=True,
        )

        for incident in incidents:
            incident_id = incident.get("incident_id", "")
            description = incident.get("description", "")
            priority = str(incident.get("priority", ""))
            status = str(incident.get("status", ""))
            application = incident.get("application", "")
            affected = incident.get("affected_users", "")

            priority_html = render_priority_badge(priority)
            status_html = render_status_badge(status)

            st.markdown(
                f"""
                <div class="incident-card">
                    <div style="display:flex; justify-content:space-between;
                                align-items:center;">
                        <span class="incident-id">{incident_id}</span>
                        <div style="display:flex; gap:8px;">
                            {priority_html}
                            {status_html}
                        </div>
                    </div>
                    <div class="incident-desc">{description}</div>
                    <div class="incident-meta">
                        <span>{application}</span>
                        <span>{affected} users affected</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "View Details",
                key=f"view_{incident_id}",
                use_container_width=True,
            ):
                st.session_state["selected_incident_id"] = incident_id
                st.rerun()
