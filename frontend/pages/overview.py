"""
Overview page -- Executive dashboard.

Displays KPI cards, monthly trends, priority distribution,
and team workload. All charts use the shared Plotly template.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.analytics.metrics import get_kpis, get_monthly_trend
from backend.analytics.trends import get_priority_distribution
from backend.analytics.workload import get_team_workload
from backend.utils.data_loader import load_historical_data, load_live_incidents
from frontend.components.cards import render_kpi_card
import frontend.styles.theme as theme


def render_overview() -> None:
    """Render the Overview executive dashboard."""
    # ── Page Header ──
    theme.render_page_header(
        "Overview",
        "Executive operational overview and key performance indicators",
    )

    # ── Load data ──
    historical = load_historical_data()
    live = load_live_incidents()
    all_data = (
        pd.concat([historical, live], ignore_index=True)
        if not live.empty
        else historical
    )

    kpis = get_kpis(all_data)
    template = theme.get_plotly_template()

    # ── KPI Row ──
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_kpi_card("Total Incidents", f"{kpis['total']:,}")
    with c2:
        render_kpi_card("Open Incidents", str(kpis["open"]))
    with c3:
        render_kpi_card("Resolved", f"{kpis['resolved']:,}")
    with c4:
        render_kpi_card("Avg Resolution", f"{kpis['avg_resolution_time']}m")
    with c5:
        render_kpi_card("Critical (P1)", f"{kpis['critical_count']:,}")
    with c6:
        render_kpi_card("Applications", str(kpis["app_count"]))

    theme.vertical_spacer(32)

    # ── Row 1: Trend + Priority ──
    col_left, col_right = st.columns(2)

    with col_left:
        trend = get_monthly_trend(historical)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=trend["month"],
                y=trend["count"],
                mode="lines+markers",
                line=dict(color=theme.ACCENT, width=2),
                marker=dict(size=4),
                name="Incidents",
            )
        )
        fig.update_layout(
            **template,
            title=dict(
                text="Monthly Incident Trend",
                font=dict(size=14, color=theme.TEXT),
            ),
            xaxis_title="",
            yaxis_title="Count",
            showlegend=False,
            height=320,
        )
        st.plotly_chart(fig, width="stretch", key="overview_trend")

    with col_right:
        pri = get_priority_distribution(historical)
        colors = [theme.PRIORITY_COLORS.get(p, theme.ACCENT) for p in pri["priority"]]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=pri["priority"],
                    values=pri["count"],
                    hole=0.55,
                    marker=dict(colors=colors),
                    textfont=dict(color=theme.TEXT, size=13),
                    textinfo="label+percent",
                )
            ]
        )
        fig.update_layout(
            **template,
            title=dict(
                text="Priority Distribution",
                font=dict(size=14, color=theme.TEXT),
            ),
            showlegend=True,
            height=320,
        )
        st.plotly_chart(fig, width="stretch", key="overview_priority")

    theme.vertical_spacer(32)

    # ── Row 2: Team Workload (Full Width) ──
    wl = get_team_workload(historical)
    fig = go.Figure(
        data=[
            go.Bar(
                x=wl["count"],
                y=wl["team"],
                orientation="h",
                marker=dict(color=theme.ACCENT),
            )
        ]
    )
    fig.update_layout(
        **template,
        title=dict(
            text="Team Workload",
            font=dict(size=14, color=theme.TEXT),
        ),
        xaxis_title="Incident Count",
        yaxis_title="",
        showlegend=False,
        height=320,
    )
    st.plotly_chart(fig, width="stretch", key="overview_workload")
