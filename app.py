"""
Incident Intelligence Platform
================================
Main application entry point.

Run with:
    streamlit run app.py
"""

from datetime import datetime

import streamlit as st

from backend.utils.data_loader import load_historical_data, load_live_incidents
from frontend.components.sidebar import render_sidebar
from frontend.pages.analytics import render_analytics
from frontend.pages.incidents import render_incidents
from frontend.pages.overview import render_overview
from frontend.pages.predictions import render_predictions
from frontend.styles.theme import TEXT, MUTED, get_global_css


def main() -> None:
    """Application entry point."""
    st.set_page_config(
        page_title="Incident Intelligence Platform",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Inject global styles ──
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # ── Sidebar navigation ──
    selected_page = render_sidebar()

    # ── Top navigation bar ──
    historical = load_historical_data()
    live = load_live_incidents()

    total = len(historical) + len(live)
    open_count = (
        int(live["status"].isin({"Open", "Assigned", "In Progress"}).sum())
        if not live.empty
        else 0
    )

    current_date = datetime.now().strftime("%B %d, %Y")

    st.markdown(
        f"""
        <div class="top-nav">
            <div>
                <div class="nav-title">Incident Intelligence</div>
                <div class="nav-date">{current_date}</div>
            </div>
            <div class="nav-stats">
                <div class="nav-stat">
                    Total<span class="stat-value">{total:,}</span>
                </div>
                <div class="nav-stat">
                    Open<span class="stat-value">{open_count}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Page routing ──
    if selected_page == "overview":
        render_overview()
    elif selected_page == "incidents":
        render_incidents()
    elif selected_page == "analytics":
        render_analytics()
    elif selected_page == "predictions":
        render_predictions()


if __name__ == "__main__":
    main()
