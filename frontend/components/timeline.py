"""
Timeline view component for the Incidents page.
Renders incidents grouped by date as styled cards with side-by-side view buttons.
"""

import streamlit as st

from frontend.components.cards import render_priority_badge, render_status_badge


def render_timeline(incidents_by_date: dict) -> None:
    """Render incidents grouped by date in a timeline layout.

    Each incident card includes an aligned *View* button that sets
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
            "No incidents present."
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

            # Renders card info on the left, and action button on the right
            col_info, col_btn = st.columns([0.8, 0.2])

            with col_info:
                st.markdown(
                    f'<div class="incident-card-info">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                    f'<span class="incident-id">{incident_id}</span>'
                    f'<div style="display:flex; gap:8px;">'
                    f'{priority_html}'
                    f'{status_html}'
                    f'</div>'
                    f'</div>'
                    f'<div class="incident-desc">{description}</div>'
                    f'<div class="incident-meta">'
                    f'<span>{application}</span> &bull; <span>{affected} users affected</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col_btn:
                # Add vertical spacing to center the button vertically next to the card
                st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
                if st.button(
                    "View",
                    key=f"view_{incident_id}",
                    use_container_width=True,
                ):
                    st.session_state["selected_incident_id"] = incident_id
                    st.rerun()
