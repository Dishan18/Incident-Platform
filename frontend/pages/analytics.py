"""
Analytics page -- Advanced operational analytics with interactive filters.

Sections: Root Cause, Resolution Time, Application, Priority, and Team.
Charts: Treemap, Box Plot, Heatmap, Stacked Bar, Trend lines.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.analytics.metrics import get_resolution_time_trend
from backend.analytics.rootcause import (
    get_resolution_by_priority,
    get_root_cause_by_team,
    get_root_cause_distribution,
)
from backend.analytics.trends import (
    get_priority_distribution,
    get_priority_trend,
)
from backend.analytics.workload import (
    get_team_priority_heatmap,
    get_team_workload,
    get_top_applications,
)
from backend.utils.data_loader import load_historical_data
from frontend.components.filters import apply_filters, render_filters
from frontend.styles.theme import (
    ACCENT,
    CARD_BG,
    CHART_COLORS,
    PRIORITY_COLORS,
    TEXT,
    get_plotly_template,
    render_page_header,
    vertical_spacer,
)


def render_analytics() -> None:
    """Render the Analytics page with filterable operational charts."""
    # ── Page Header ──
    render_page_header(
        "Analytics",
        "Advanced operational analytics and insights",
    )

    # ── Data + Filters ──
    df = load_historical_data()
    filters = render_filters(df)
    df = apply_filters(df, filters)
    template = get_plotly_template()

    if df.empty:
        st.info("No data matches the selected filters.")
        return

    vertical_spacer(24)

    # ── Organizing Charts into Tabs (No Emojis) ──
    tab_trends, tab_workload, tab_performance = st.tabs([
        "Volume & Trends",
        "Team Workload",
        "Performance",
    ])

    # ──────────────────────────────────────────────
    # Tab 1: Volume & Trends
    # ──────────────────────────────────────────────
    with tab_trends:
        vertical_spacer(16)

        # Top Applications (Full Width)
        apps = get_top_applications(df, n=15)
        if not apps.empty:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=apps["application"],
                        y=apps["count"],
                        marker=dict(color=CHART_COLORS[1]),
                    )
                ]
            )
            fig.update_layout(
                **template,
                title=dict(
                    text="Top Applications by Incident Volume",
                    font=dict(size=14, color=TEXT),
                ),
                xaxis_title="",
                yaxis_title="Count",
                showlegend=False,
                height=340,
            )
            st.plotly_chart(
                fig, use_container_width=True, key="analytics_apps"
            )

        vertical_spacer(32)

        # Priority Trend & Priority Distribution side-by-side
        col1, col2 = st.columns(2)

        with col1:
            ptrend = get_priority_trend(df)
            if not ptrend.empty:
                fig = px.bar(
                    ptrend,
                    x="month",
                    y="count",
                    color="priority",
                    color_discrete_map=PRIORITY_COLORS,
                    category_orders={"priority": ["P1", "P2", "P3", "P4"]},
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Priority Trend (Stacked)",
                        font=dict(size=14, color=TEXT),
                    ),
                    barmode="stack",
                    xaxis_title="",
                    yaxis_title="Count",
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_pri_trend"
                )

        with col2:
            pri_dist = get_priority_distribution(df)
            if not pri_dist.empty:
                colors = [
                    PRIORITY_COLORS.get(p, ACCENT) for p in pri_dist["priority"]
                ]
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=pri_dist["priority"],
                            values=pri_dist["count"],
                            hole=0.55,
                            marker=dict(colors=colors),
                            textfont=dict(color=TEXT),
                        )
                    ]
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Priority Distribution",
                        font=dict(size=14, color=TEXT),
                    ),
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_pri_donut"
                )

    # ──────────────────────────────────────────────
    # Tab 2: Team Workload & Root Causes
    # ──────────────────────────────────────────────
    with tab_workload:
        vertical_spacer(16)

        col1, col2 = st.columns(2)

        with col1:
            wl = get_team_workload(df)
            if not wl.empty:
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=wl["count"],
                            y=wl["team"],
                            orientation="h",
                            marker=dict(color=ACCENT),
                        )
                    ]
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Team Workload",
                        font=dict(size=14, color=TEXT),
                    ),
                    xaxis_title="Incident Count",
                    showlegend=False,
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_wl"
                )

        with col2:
            heatmap = get_team_priority_heatmap(df)
            if not heatmap.empty:
                fig = go.Figure(
                    data=go.Heatmap(
                        z=heatmap.values,
                        x=heatmap.columns.tolist(),
                        y=heatmap.index.tolist(),
                        colorscale=[[0, CARD_BG], [1, ACCENT]],
                        texttemplate="%{z:.0f}",
                        textfont=dict(color=TEXT, size=12),
                        showscale=False,
                    )
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Team vs Priority Heatmap",
                        font=dict(size=14, color=TEXT),
                    ),
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_heatmap"
                )

        vertical_spacer(32)

        # Root Causes by Team (Full Width)
        rc_team = get_root_cause_by_team(df)
        if not rc_team.empty:
            fig = px.treemap(
                rc_team,
                path=["team", "root_cause"],
                values="count",
                color_discrete_sequence=CHART_COLORS,
            )
            fig.update_layout(
                **template,
                title=dict(
                    text="Root Causes by Team",
                    font=dict(size=14, color=TEXT),
                ),
                height=450,
            )
            fig.update_traces(
                textfont=dict(color=TEXT),
                marker=dict(cornerradius=4),
            )
            st.plotly_chart(
                fig, use_container_width=True, key="analytics_rc_tree"
            )

    # ──────────────────────────────────────────────
    # Tab 3: Performance & Root Causes
    # ──────────────────────────────────────────────
    with tab_performance:
        vertical_spacer(16)

        col1, col2 = st.columns(2)

        with col1:
            res_data = get_resolution_by_priority(df)
            if not res_data.empty:
                fig = px.box(
                    res_data,
                    x="priority",
                    y="resolution_time",
                    color="priority",
                    color_discrete_map=PRIORITY_COLORS,
                    category_orders={"priority": ["P1", "P2", "P3", "P4"]},
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Resolution Time by Priority",
                        font=dict(size=14, color=TEXT),
                    ),
                    xaxis_title="Priority",
                    yaxis_title="Minutes",
                    showlegend=False,
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_res_box"
                )

        with col2:
            rc_dist = get_root_cause_distribution(df)
            if not rc_dist.empty:
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=rc_dist["count"],
                            y=rc_dist["root_cause"],
                            orientation="h",
                            marker=dict(color=CHART_COLORS[0]),
                        )
                    ]
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Root Cause Distribution",
                        font=dict(size=14, color=TEXT),
                    ),
                    height=400,
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_rc_bar"
                )
