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
    ("Future Search", "search"),
]


def render_sidebar() -> str:
    """Render sidebar navigation and return the selected page key.

    The *Future Search* option is displayed but disabled with an
    informational note.
    """
    with st.sidebar:
        st.markdown(
            '<div style="padding: 0 16px 24px 16px;">'
            '<div style="font-size: 18px; font-weight: 700; color: #F3F4F6;'
            ' letter-spacing: -0.02em;">'
            "Incident Intelligence"
            "</div>"
            '<div style="font-size: 12px; color: #9CA3AF; margin-top: 4px;">'
            "Operations Platform"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

        labels = [item[0] for item in NAV_ITEMS]
        selected_label = st.radio(
            "Navigation",
            labels,
            label_visibility="collapsed",
        )

        if selected_label == "Future Search":
            st.info("Semantic search will be available in a future release.")
            selected_label = st.session_state.get("_last_page", "Overview")
        else:
            st.session_state["_last_page"] = selected_label

        for label, key in NAV_ITEMS:
            if label == selected_label:
                return key

    return "overview"
