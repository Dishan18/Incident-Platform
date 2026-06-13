"""
Sidebar navigation component.
Renders the permanent left sidebar with page navigation.
"""

import streamlit as st


NAV_ITEMS: list[tuple[str, str]] = [
    ("Overview", "overview"),
    ("Incidents", "incidents"),
    ("Analytics", "analytics"),
    ("Predictions", "predictions"),
]


def render_sidebar() -> str:
    """Render sidebar navigation and return the selected page key."""
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-brand">'
            '<div class="brand-title">Incident Intelligence</div>'
            '<div class="brand-subtitle">Operations Platform</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        labels = [item[0] for item in NAV_ITEMS]
        selected_label = st.radio(
            "Navigation",
            labels,
            label_visibility="collapsed",
        )

        st.session_state["_last_page"] = selected_label

        for label, key in NAV_ITEMS:
            if label == selected_label:
                return key

    return "overview"

