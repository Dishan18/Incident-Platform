"""
Reusable card components for KPIs, badges, and prediction outputs.
All rendering uses injected HTML with CSS classes from the theme.
"""

import streamlit as st


def render_kpi_card(label: str, value: str, subtitle: str = "") -> None:
    """Render a styled KPI metric card using custom HTML."""
    subtitle_html = (
        f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_priority_badge(priority: str) -> str:
    """Return an HTML string for a priority badge (P1-P4)."""
    css_class = (
        f"badge-{priority.lower()}"
        if priority in ("P1", "P2", "P3", "P4")
        else ""
    )
    return f'<span class="badge {css_class}">{priority}</span>'


def render_status_badge(status: str) -> str:
    """Return an HTML string for a status badge."""
    css_map = {
        "Open": "status-open",
        "Assigned": "status-assigned",
        "In Progress": "status-inprogress",
        "Resolved": "status-resolved",
        "Closed": "status-closed",
        "Cancelled": "status-cancelled",
    }
    css_class = css_map.get(status, "")
    return f'<span class="badge {css_class}">{status}</span>'


def render_prediction_card(
    label: str, value: str, confidence: str = ""
) -> None:
    """Render a prediction output card with an optional confidence score."""
    conf_html = (
        f'<div class="pred-confidence">Confidence: {confidence}</div>'
        if confidence
        else ""
    )
    st.markdown(
        f"""
        <div class="prediction-card">
            <div class="pred-label">{label}</div>
            <div class="pred-value">{value}</div>
            {conf_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
